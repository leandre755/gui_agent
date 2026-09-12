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

async fn resolve_ref(object_ref_or_index: &str, cached: Option<&[AccessibilityNode]>) -> Result<String> {
    if let Ok(idx) = object_ref_or_index.parse::<u32>() {
        if let Some(nodes) = cached {
            return nodes
                .iter()
                .find(|n| n.index == idx)
                .map(|n| n.object_ref.clone())
                .ok_or_else(|| anyhow!("Aucun nœud d'accessibilité trouvé dans le cache pour l'index {idx}"));
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
        "apps" => {
            match list_accessible_apps(50).await {
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
            }
        }
        "doctor" => {
            match connect().await {
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
                }
            }
        }
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

async fn run_mcp_server() -> Result<()> {
    let stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut reader = BufReader::new(stdin).lines();
    let cached_nodes: Arc<Mutex<Vec<AccessibilityNode>>> = Arc::new(Mutex::new(Vec::new()));

    while let Ok(Some(line)) = reader.next_line().await {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }

        let parsed: Value = match serde_json::from_str(trimmed) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let method = parsed.get("method").and_then(Value::as_str).unwrap_or("");
        let id = parsed.get("id").cloned();

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
                stdout.write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes()).await?;
                stdout.flush().await?;
            }
            "notifications/initialized" => {
                // MCP client notification, no response required
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
                                let mut cache = cached_nodes.lock().await;
                                *cache = nodes.clone();
                                (
                                    serde_json::json!({
                                        "status": "success",
                                        "count": nodes.len(),
                                        "tree": nodes,
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
                        let target = arguments
                            .get("element_identifier")
                            .and_then(Value::as_str)
                            .map(ToString::to_string)
                            .or_else(|| {
                                arguments
                                    .get("element_index")
                                    .and_then(Value::as_u64)
                                    .map(|idx| idx.to_string())
                            });

                        if let Some(target_ref) = target {
                            let cache = cached_nodes.lock().await;
                            match resolve_ref(&target_ref, Some(&cache)).await {
                                Ok(resolved) => {
                                    drop(cache);
                                    match perform_action(&resolved, action_name).await {
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
                                    }
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
                        } else {
                            (
                                serde_json::json!({
                                    "status": "error",
                                    "error": "Paramètres element_index ou element_identifier requis",
                                    "ok": false
                                }),
                                true,
                            )
                        }
                    }
                    "set_value" => {
                        let val = arguments.get("value").and_then(Value::as_str).unwrap_or("");
                        let target = arguments
                            .get("element_identifier")
                            .and_then(Value::as_str)
                            .map(ToString::to_string)
                            .or_else(|| {
                                arguments
                                    .get("element_index")
                                    .and_then(Value::as_u64)
                                    .map(|idx| idx.to_string())
                            });

                        if let Some(target_ref) = target {
                            let cache = cached_nodes.lock().await;
                            match resolve_ref(&target_ref, Some(&cache)).await {
                                Ok(resolved) => {
                                    drop(cache);
                                    match set_element_value(&resolved, val).await {
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
                                    }
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
                        } else {
                            (
                                serde_json::json!({
                                    "status": "error",
                                    "error": "Paramètres element_index ou element_identifier requis",
                                    "ok": false
                                }),
                                true,
                            )
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
                stdout.write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes()).await?;
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
                    stdout.write_all(format!("{}\n", serde_json::to_string(&resp)?).as_bytes()).await?;
                    stdout.flush().await?;
                }
            }
        }
    }

    Ok(())
}
