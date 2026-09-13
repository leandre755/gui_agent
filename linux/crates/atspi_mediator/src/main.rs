//! Point d'entrée CLI et serveur MCP pour le médiateur AT-SPI gui_agent.

use anyhow::{anyhow, Result};
use atspi_mediator::{
    connect, hydrate_session_bus_env, list_accessible_apps, perform_action, set_element_value,
    snapshot_tree, AccessibilityNode,
};
use serde_json::Value;
use std::env;
use std::sync::Arc;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::sync::Mutex;

async fn resolve_ref(
    object_ref_or_index: &str,
    cached: Option<&[AccessibilityNode]>,
) -> Result<String> {
    if let Ok(idx) = object_ref_or_index.parse::<u32>() {
        if let Some(nodes) = cached {
            return nodes
                .iter()
                .find(|n| n.index == idx)
                .map(|n| n.object_ref.clone())
                .ok_or_else(|| {
                    anyhow!("Aucun nœud d'accessibilité trouvé dans le cache pour l'index {idx}")
                });
        }
        Err(anyhow!(
            "L'index numérique '{idx}' nécessite un cache de snapshot actif. Veuillez fournir une référence AT-SPI explicite (ex: ':1.42/path')."
        ))
    } else {
        Ok(object_ref_or_index.to_string())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    hydrate_session_bus_env();
    let args: Vec<String> = env::args().collect();
    let command = args.get(1).map(String::as_str).unwrap_or("help");

    match command {
        "state" => {
            let app_name = args.get(2).map(String::as_str);
            match snapshot_tree(app_name, None, 1000, 32).await {
                Ok(nodes) => {
                    let out = serde_json::json!({
                        "status": "success",
                        "count": nodes.len(),
                        "tree": nodes,
                    });
                    println!("{}", serde_json::to_string(&out)?);
                }
                Err(err) => {
                    let out = serde_json::json!({
                        "status": "error",
                        "error": format!("{err:#}"),
                    });
                    eprintln!("{}", serde_json::to_string(&out)?);
                    std::process::exit(1);
                }
            }
        }
        "action" => {
            let Some(target) = args.get(2) else {
                eprintln!("Usage: gui-agent-atspi action <object_ref> [action_name]");
                std::process::exit(1);
            };
            let action_name = args.get(3).map(String::as_str);
            let object_ref = match resolve_ref(target, None).await {
                Ok(r) => r,
                Err(err) => {
                    let out = serde_json::json!({
                        "status": "error",
                        "error": format!("{err:#}"),
                    });
                    eprintln!("{}", serde_json::to_string(&out)?);
                    std::process::exit(1);
                }
            };
            match perform_action(&object_ref, action_name).await {
                Ok(inv) => {
                    let out = serde_json::json!({
                        "status": "success",
                        "action_index": inv.action_index,
                        "action_name": inv.action_name,
                        "ok": inv.ok,
                    });
                    println!("{}", serde_json::to_string(&out)?);
                }
                Err(err) => {
                    let out = serde_json::json!({
                        "status": "error",
                        "error": format!("{err:#}"),
                    });
                    eprintln!("{}", serde_json::to_string(&out)?);
                    std::process::exit(1);
                }
            }
        }
        "value" => {
            let Some(target) = args.get(2) else {
                eprintln!("Usage: gui-agent-atspi value <object_ref> <value>");
                std::process::exit(1);
            };
            let Some(val) = args.get(3) else {
                eprintln!("Usage: gui-agent-atspi value <object_ref> <value>");
                std::process::exit(1);
            };
            let object_ref = match resolve_ref(target, None).await {
                Ok(r) => r,
                Err(err) => {
                    let out = serde_json::json!({
                        "status": "error",
                        "error": format!("{err:#}"),
                    });
                    eprintln!("{}", serde_json::to_string(&out)?);
                    std::process::exit(1);
                }
            };
            match set_element_value(&object_ref, val).await {
                Ok(inv) => {
                    let out = serde_json::json!({
                        "status": "success",
                        "result": format!("{inv:?}"),
                        "ok": true,
                    });
                    println!("{}", serde_json::to_string(&out)?);
                }
                Err(err) => {
                    let out = serde_json::json!({
                        "status": "error",
                        "error": format!("{err:#}"),
                        "ok": false,
                    });
                    eprintln!("{}", serde_json::to_string(&out)?);
                    std::process::exit(1);
                }
            }
        }
        "apps" => match list_accessible_apps(50).await {
            Ok(apps) => {
                let out = serde_json::json!({
                    "status": "success",
                    "apps": apps,
                });
                println!("{}", serde_json::to_string(&out)?);
            }
            Err(err) => {
                let out = serde_json::json!({
                    "status": "error",
                    "error": format!("{err:#}"),
                });
                eprintln!("{}", serde_json::to_string(&out)?);
                std::process::exit(1);
            }
        },
        "doctor" => match connect().await {
            Ok(_) => {
                let out = serde_json::json!({
                    "status": "success",
                    "at_spi_available": true,
                });
                println!("{}", serde_json::to_string(&out)?);
            }
            Err(err) => {
                let out = serde_json::json!({
                    "status": "error",
                    "at_spi_available": false,
                    "error": format!("{err:#}"),
                });
                println!("{}", serde_json::to_string(&out)?);
                std::process::exit(1);
            }
        },
        "mcp" => {
            run_mcp_server().await?;
        }
        _ => {
            eprintln!("gui-agent-atspi: AT-SPI2 / D-Bus accessibility bridge CLI & MCP server");
            eprintln!("Commandes disponibles : state, action, value, apps, doctor, mcp");
            std::process::exit(1);
        }
    }

    Ok(())
}

#[derive(Clone)]
struct SnapshotState {
    token: String,
    nodes: Vec<AccessibilityNode>,
}

fn resolve_mcp_target(
    arguments: &Value,
    cache: &Option<SnapshotState>,
) -> Result<String, (Value, bool)> {
    let target_ident = arguments.get("element_identifier").and_then(Value::as_str);
    let target_index = arguments.get("element_index").and_then(Value::as_u64);
    let snapshot_token = arguments.get("snapshot_token").and_then(Value::as_str);

    let numeric_idx = target_index
        .map(|i| i as u32)
        .or_else(|| target_ident.and_then(|id| id.parse::<u32>().ok()));

    if let Some(idx) = numeric_idx {
        let Some(snap) = cache else {
            return Err((
                serde_json::json!({
                    "status": "error",
                    "error": "Aucun snapshot actif. Veuillez d'abord appeler get_app_state.",
                    "ok": false
                }),
                true,
            ));
        };
        let Some(token) = snapshot_token else {
            return Err((
                serde_json::json!({
                    "status": "error",
                    "error": "L'utilisation d'un index numérique (element_index) requiert le paramètre snapshot_token pour éviter d'agir sur un contrôle obsolète.",
                    "ok": false
                }),
                true,
            ));
        };
        if token != snap.token {
            return Err((
                serde_json::json!({
                    "status": "error",
                    "error": format!("snapshot_token périmé ('{token}' != '{}'). Veuillez rafraîchir get_app_state.", snap.token),
                    "ok": false
                }),
                true,
            ));
        }
        let node = snap.nodes.iter().find(|n| n.index == idx);
        let Some(node) = node else {
            return Err((
                serde_json::json!({
                    "status": "error",
                    "error": format!("Index {idx} introuvable dans le snapshot actuel ({})", snap.token),
                    "ok": false
                }),
                true,
            ));
        };
        Ok(node.object_ref.clone())
    } else if let Some(ident) = target_ident {
        if ident.is_empty() {
            Err((
                serde_json::json!({
                    "status": "error",
                    "error": "L'identifiant d'élément (element_identifier) ne peut pas être vide.",
                    "ok": false
                }),
                true,
            ))
        } else {
            Ok(ident.to_string())
        }
    } else {
        Err((
            serde_json::json!({
                "status": "error",
                "error": "Paramètres element_index ou element_identifier requis.",
                "ok": false
            }),
            true,
        ))
    }
}

async fn run_mcp_server() -> Result<()> {
    let stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut reader = BufReader::new(stdin).lines();
    let cached_snapshot: Arc<Mutex<Option<SnapshotState>>> = Arc::new(Mutex::new(None));
    let snapshot_seq = Arc::new(std::sync::atomic::AtomicU64::new(1));

    loop {
        let line = match reader.next_line().await {
            Ok(Some(line)) => line,
            Ok(None) => break,
            Err(err) => {
                eprintln!("gui-agent-atspi: erreur de lecture stdin : {err}");
                break;
            }
        };
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }

        let parsed: Value = match serde_json::from_str(trimmed) {
            Ok(v) => v,
            Err(_) => {
                let err_resp = serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": Value::Null,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                });
                stdout
                    .write_all(format!("{}\n", serde_json::to_string(&err_resp)?).as_bytes())
                    .await?;
                stdout.flush().await?;
                continue;
            }
        };

        if !parsed.is_object() {
            let err_resp = serde_json::json!({
                "jsonrpc": "2.0",
                "id": Value::Null,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request"
                }
            });
            stdout
                .write_all(format!("{}\n", serde_json::to_string(&err_resp)?).as_bytes())
                .await?;
            stdout.flush().await?;
            continue;
        }

        let method = parsed.get("method").and_then(Value::as_str).unwrap_or("");
        let id = parsed.get("id").cloned();

        // Ignorer les notifications sans id (ex: notifications/initialized)
        if id.is_none() || id == Some(Value::Null) {
            continue;
        }

        match method {
            "initialize" => {
                let resp = serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "gui-agent-atspi",
                            "version": "0.1.0"
                        }
                    }
                });
                stdout
                    .write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes())
                    .await?;
                stdout.flush().await?;
            }
            "tools/list" => {
                let resp = serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "tools": [
                            {
                                "name": "get_app_state",
                                "description": "Extracts the accessibility tree for a given desktop application or desktop root",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "app_name": {
                                            "type": "string",
                                            "description": "Optional application name or window title to filter by"
                                        }
                                    }
                                }
                            },
                            {
                                "name": "perform_action",
                                "description": "Performs an action on an accessible element identified by element_identifier or element_index",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "element_identifier": {
                                            "type": "string",
                                            "description": "D-Bus object path of the accessible element"
                                        },
                                        "element_index": {
                                            "type": "integer",
                                            "description": "Numeric index from the latest get_app_state snapshot"
                                        },
                                        "action": {
                                            "type": "string",
                                            "description": "Action name to perform, defaults to activate"
                                        },
                                        "snapshot_token": {
                                            "type": "string",
                                            "description": "Snapshot token returned by get_app_state (required when targeting by element_index)"
                                        }
                                    }
                                }
                            },
                            {
                                "name": "set_value",
                                "description": "Sets the text content or numeric value of an accessible element",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "element_identifier": {
                                            "type": "string",
                                            "description": "D-Bus object path of the accessible element"
                                        },
                                        "element_index": {
                                            "type": "integer",
                                            "description": "Numeric index from the latest get_app_state snapshot"
                                        },
                                        "snapshot_token": {
                                            "type": "string",
                                            "description": "Snapshot token returned by get_app_state (required when targeting by element_index)"
                                        },
                                        "value": {
                                            "type": "string",
                                            "description": "Value to assign to the accessible element"
                                        }
                                    },
                                    "required": ["value"]
                                }
                            }
                        ]
                    }
                });
                stdout
                    .write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes())
                    .await?;
                stdout.flush().await?;
            }
            "tools/call" => {
                let params = parsed.get("params").cloned().unwrap_or(Value::Null);
                let tool_name = params.get("name").and_then(Value::as_str).unwrap_or("");
                let arguments = params.get("arguments").cloned().unwrap_or(Value::Null);

                let (result_data, is_error) = match tool_name {
                    "get_app_state" => {
                        let app_name = arguments.get("app_name").and_then(Value::as_str);
                        match snapshot_tree(app_name, None, 1000, 32).await {
                            Ok(nodes) => {
                                let token = format!(
                                    "snap-{}",
                                    snapshot_seq.fetch_add(1, std::sync::atomic::Ordering::SeqCst)
                                );
                                let mut cache = cached_snapshot.lock().await;
                                *cache = Some(SnapshotState {
                                    token: token.clone(),
                                    nodes: nodes.clone(),
                                });
                                (
                                    serde_json::json!({
                                        "status": "success",
                                        "count": nodes.len(),
                                        "tree": nodes,
                                        "snapshot_token": token,
                                        "ok": true
                                    }),
                                    false,
                                )
                            }
                            Err(err) => (
                                serde_json::json!({
                                    "status": "error",
                                    "error": format!("{err:#}"),
                                    "ok": false
                                }),
                                true,
                            ),
                        }
                    }
                    "perform_action" => {
                        let action_name = arguments.get("action").and_then(Value::as_str);
                        let cache = cached_snapshot.lock().await;
                        let target_res = resolve_mcp_target(&arguments, &cache);
                        drop(cache);

                        match target_res {
                            Ok(resolved) => match perform_action(&resolved, action_name).await {
                                Ok(inv) => (
                                    serde_json::json!({
                                        "status": "success",
                                        "ok": inv.ok,
                                        "action_index": inv.action_index,
                                        "action_name": inv.action_name
                                    }),
                                    !inv.ok,
                                ),
                                Err(err) => (
                                    serde_json::json!({
                                        "status": "error",
                                        "error": format!("{err:#}"),
                                        "ok": false
                                    }),
                                    true,
                                ),
                            },
                            Err(err_tuple) => err_tuple,
                        }
                    }
                    "set_value" => {
                        let val = arguments.get("value").and_then(Value::as_str).unwrap_or("");
                        let cache = cached_snapshot.lock().await;
                        let target_res = resolve_mcp_target(&arguments, &cache);
                        drop(cache);

                        match target_res {
                            Ok(resolved) => match set_element_value(&resolved, val).await {
                                Ok(inv) => (
                                    serde_json::json!({
                                        "status": "success",
                                        "ok": true,
                                        "result": format!("{inv:?}")
                                    }),
                                    false,
                                ),
                                Err(err) => (
                                    serde_json::json!({
                                        "status": "error",
                                        "error": format!("{err:#}"),
                                        "ok": false
                                    }),
                                    true,
                                ),
                            },
                            Err(err_tuple) => err_tuple,
                        }
                    }
                    _ => (
                        serde_json::json!({
                            "status": "error",
                            "error": format!("Outil inconnu : {tool_name}"),
                            "ok": false
                        }),
                        true,
                    ),
                };

                let resp = serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "isError": is_error,
                        "structuredContent": result_data,
                        "content": [
                            {
                                "type": "text",
                                "text": serde_json::to_string(&result_data).unwrap_or_default()
                            }
                        ]
                    }
                });
                stdout
                    .write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes())
                    .await?;
                stdout.flush().await?;
            }
            _ => {
                if let Some(id_val) = id {
                    let resp = serde_json::json!({
                        "jsonrpc": "2.0",
                        "id": id_val,
                        "error": {
                            "code": -32601,
                            "message": format!("Method not found: {method}")
                        }
                    });
                    stdout
                        .write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes())
                        .await?;
                    stdout.flush().await?;
                }
            }
        }
    }

    Ok(())
}
