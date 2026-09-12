//! AT-SPI2 / D-Bus accessibility mediation engine for gui_agent.

use anyhow::{anyhow, Context, Result};
use atspi::{
    proxy::{
        accessible::{AccessibleProxy, ObjectRefExt},
        proxy_ext::ProxyExt,
    },
    CoordType, ObjectRef, ObjectRefOwned, StateSet,
};
use atspi_connection::AccessibilityConnection;
use futures_util::{stream, StreamExt};
use serde::{Deserialize, Serialize};
use std::{collections::VecDeque, future::Future, time::Duration};
use tokio::time::timeout;
use zbus::{
    fdo::DBusProxy,
    names::{BusName, UniqueName},
    zvariant::ObjectPath,
};

const MAX_TEXT_READBACK_CHARS: i32 = 4096;
const MAX_TEXT_SELECTIONS: i32 = 8;
const DEFAULT_SNAPSHOT_MAX_NODES: usize = 1_000;
const HARD_SNAPSHOT_MAX_NODES: usize = 2_000;
const DEFAULT_SNAPSHOT_MAX_DEPTH: u32 = 32;
const HARD_SNAPSHOT_MAX_DEPTH: u32 = 64;
const CHILD_READ_CONCURRENCY: usize = 16;
const SNAPSHOT_TIMEOUT: Duration = Duration::from_secs(10);
const MAX_DISCOVERY_ROOTS: usize = 256;
const ROOT_MATCH_CHILD_LIMIT: usize = 8;
const MAX_DISCOVERY_CHILD_READS: usize = MAX_DISCOVERY_ROOTS * ROOT_MATCH_CHILD_LIMIT;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibleAppSummary {
    pub object_ref: String,
    pub name: Option<String>,
    pub pid: Option<u32>,
    pub role: String,
    pub child_count: i32,
    pub bounds: Option<Bounds>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibilityNode {
    pub index: u32,
    pub parent_index: Option<u32>,
    pub depth: u32,
    pub object_ref: String,
    pub role: String,
    pub name: Option<String>,
    pub description: Option<String>,
    pub child_count: i32,
    pub bounds: Option<Bounds>,
    pub states: Vec<String>,
    pub actions: Vec<AccessibilityAction>,
    pub value: Option<AccessibilityValue>,
    pub text: Option<AccessibilityText>,
    pub supports_editable_text: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bounds {
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibilityAction {
    pub index: i32,
    pub name: String,
    pub description: String,
    pub keybinding: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibilityValue {
    pub current: f64,
    pub minimum: f64,
    pub maximum: f64,
    pub minimum_increment: f64,
    pub text: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibilityText {
    pub character_count: i32,
    pub caret_offset: Option<i32>,
    pub content: Option<String>,
    pub truncated: bool,
    pub selections: Vec<AccessibilityTextSelection>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessibilityTextSelection {
    pub start_offset: i32,
    pub end_offset: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionInvocation {
    pub action_index: i32,
    pub action_name: Option<String>,
    pub ok: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValueSetInvocation {
    Numeric { value: f64 },
    EditableText,
}

pub fn hydrate_session_bus_env() {
    if std::env::var_os("DBUS_SESSION_BUS_ADDRESS").is_none() {
        if let Ok(runtime) = std::env::var("XDG_RUNTIME_DIR") {
            let bus = std::path::Path::new(&runtime).join("bus");
            if bus.exists() {
                std::env::set_var(
                    "DBUS_SESSION_BUS_ADDRESS",
                    format!("unix:path={}", bus.display()),
                );
            }
        }
    }
}

pub fn snapshot_limits(
    requested_max_nodes: Option<usize>,
    requested_max_depth: Option<u32>,
) -> (usize, u32) {
    (
        requested_max_nodes
            .unwrap_or(DEFAULT_SNAPSHOT_MAX_NODES)
            .clamp(1, HARD_SNAPSHOT_MAX_NODES),
        requested_max_depth
            .unwrap_or(DEFAULT_SNAPSHOT_MAX_DEPTH)
            .min(HARD_SNAPSHOT_MAX_DEPTH),
    )
}

fn snapshot_child_read_budgets(max_nodes: usize) -> (usize, usize, usize) {
    (MAX_DISCOVERY_ROOTS, MAX_DISCOVERY_CHILD_READS, max_nodes)
}

struct BoundedTraversal<T> {
    queue: VecDeque<T>,
    attempted: usize,
    max_items: usize,
}

impl<T> BoundedTraversal<T> {
    fn new(max_items: usize) -> Self {
        Self {
            queue: VecDeque::new(),
            attempted: 0,
            max_items,
        }
    }

    fn enqueue(&mut self, items: impl IntoIterator<Item = T>) {
        self.queue
            .extend(items.into_iter().take(self.remaining_capacity()));
    }

    fn pop(&mut self) -> Option<T> {
        if self.attempted >= self.max_items {
            return None;
        }
        let item = self.queue.pop_front()?;
        self.attempted += 1;
        Some(item)
    }

    fn remaining_capacity(&self) -> usize {
        self.max_items
            .saturating_sub(self.attempted.saturating_add(self.queue.len()))
    }
}

fn bounded_child_count(reported: i32, limit: usize) -> usize {
    usize::try_from(reported).unwrap_or_default().min(limit)
}

struct IndexedReadBatch<T> {
    items: Vec<T>,
    attempted: usize,
}

impl<T> IndexedReadBatch<T> {
    fn all_failed(&self) -> bool {
        self.attempted > 0 && self.items.is_empty()
    }
}

async fn fetch_indexed_up_to<T, E, F, Fut>(
    reported: i32,
    limit: usize,
    remaining_attempts: &mut usize,
    fetch: F,
) -> IndexedReadBatch<T>
where
    F: Fn(i32) -> Fut,
    Fut: Future<Output = std::result::Result<T, E>>,
{
    let attempt_count = bounded_child_count(reported, limit).min(*remaining_attempts);
    *remaining_attempts = (*remaining_attempts).saturating_sub(attempt_count);
    let end_index = i32::try_from(attempt_count).unwrap_or(i32::MAX);

    let items = stream::iter(0..end_index)
        .map(fetch)
        .buffered(CHILD_READ_CONCURRENCY)
        .filter_map(|result| async move { result.ok() })
        .collect()
        .await;

    IndexedReadBatch {
        items,
        attempted: attempt_count,
    }
}

async fn children_up_to(
    proxy: &AccessibleProxy<'_>,
    limit: usize,
    remaining_attempts: &mut usize,
) -> std::result::Result<IndexedReadBatch<ObjectRefOwned>, atspi::AtspiError> {
    if limit == 0 || *remaining_attempts == 0 {
        return Ok(IndexedReadBatch {
            items: Vec::new(),
            attempted: 0,
        });
    }

    let child_count = proxy.child_count().await?;
    Ok(
        fetch_indexed_up_to(child_count, limit, remaining_attempts, |index| {
            proxy.get_child_at_index(index)
        })
        .await,
    )
}

pub async fn connect() -> Result<AccessibilityConnection> {
    hydrate_session_bus_env();
    AccessibilityConnection::new()
        .await
        .context("Échec de connexion au bus d'accessibilité AT-SPI (org.a11y.Bus)")
}

async fn open_accessible<'r>(
    conn: &AccessibilityConnection,
    object_ref: &'r ObjectRefOwned,
) -> Result<AccessibleProxy<'r>, atspi::AtspiError> {
    object_ref.as_accessible_proxy(conn.connection()).await
}

async fn registry_children(
    conn: &AccessibilityConnection,
    limit: usize,
    remaining_child_reads: &mut usize,
) -> Result<Vec<ObjectRefOwned>> {
    let root = conn
        .root_accessible_on_registry()
        .await
        .context("Impossible d'ouvrir la racine AT-SPI du registre")?;
    let batch = children_up_to(&root, limit, remaining_child_reads)
        .await
        .context("Impossible de lire les enfants du registre AT-SPI")?;
    if batch.all_failed() {
        return Err(anyhow!(
            "Le registre AT-SPI a signalé des enfants, mais chaque lecture a échoué"
        ));
    }
    Ok(batch.items)
}

async fn object_ref_pid(dbus: Option<&DBusProxy<'_>>, object_ref: &ObjectRefOwned) -> Option<u32> {
    let dbus = dbus?;
    let bus_name = BusName::try_from(object_ref.name_as_str()?.to_string()).ok()?;
    dbus.get_connection_unix_process_id(bus_name).await.ok()
}

async fn select_roots(
    conn: &AccessibilityConnection,
    roots: Vec<ObjectRefOwned>,
    app_name_or_bundle_identifier: Option<&str>,
    target_pid: Option<u32>,
    remaining_child_reads: &mut usize,
) -> Vec<ObjectRefOwned> {
    let needle = app_name_or_bundle_identifier
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(|value| value.to_ascii_lowercase());
    let dbus = DBusProxy::new(conn.connection()).await.ok();
    let mut remaining = roots;

    if let Some(target_pid) = target_pid {
        let mut pid_and_filter_matches = Vec::new();
        let mut pid_matches = Vec::new();
        let mut non_pid_matches = Vec::new();

        for object_ref in remaining {
            if object_ref_pid(dbus.as_ref(), &object_ref).await == Some(target_pid) {
                if let Some(needle) = needle.as_deref() {
                    if root_matches(conn, &object_ref, needle, remaining_child_reads).await {
                        pid_and_filter_matches.push(object_ref);
                    } else {
                        pid_matches.push(object_ref);
                    }
                } else {
                    pid_matches.push(object_ref);
                }
            } else {
                non_pid_matches.push(object_ref);
            }
        }

        if !pid_and_filter_matches.is_empty() {
            return pid_and_filter_matches;
        }
        if !pid_matches.is_empty() {
            return pid_matches;
        }
        remaining = non_pid_matches;
    }

    if let Some(needle) = needle.as_deref() {
        let mut filter_matches = Vec::new();
        for object_ref in remaining {
            if root_matches(conn, &object_ref, needle, remaining_child_reads).await {
                filter_matches.push(object_ref);
            }
        }
        return filter_matches;
    }

    remaining
}

async fn root_matches(
    conn: &AccessibilityConnection,
    object_ref: &ObjectRefOwned,
    needle: &str,
    remaining_child_reads: &mut usize,
) -> bool {
    let Ok(proxy) = open_accessible(conn, object_ref).await else {
        return object_ref_id(object_ref)
            .to_ascii_lowercase()
            .contains(needle);
    };

    if proxy_matches(&proxy, object_ref, needle).await {
        return true;
    }

    for child_ref in children_up_to(&proxy, ROOT_MATCH_CHILD_LIMIT, remaining_child_reads)
        .await
        .map(|batch| batch.items)
        .unwrap_or_default()
    {
        let Ok(child_proxy) = open_accessible(conn, &child_ref).await else {
            continue;
        };
        if proxy_matches(&child_proxy, &child_ref, needle).await {
            return true;
        }
    }

    false
}

async fn proxy_matches(
    proxy: &AccessibleProxy<'_>,
    object_ref: &ObjectRefOwned,
    needle: &str,
) -> bool {
    let name = proxy.name().await.unwrap_or_default();
    let role = proxy.get_role_name().await.unwrap_or_default();
    format!("{} {} {}", object_ref_id(object_ref), name, role)
        .to_ascii_lowercase()
        .contains(needle)
}

pub async fn list_accessible_apps(limit: usize) -> Result<Vec<AccessibleAppSummary>> {
    let conn = connect().await?;
    let mut remaining_child_reads = limit;
    let roots = registry_children(&conn, limit, &mut remaining_child_reads).await?;
    let dbus = DBusProxy::new(conn.connection()).await.ok();
    let mut apps = Vec::new();

    for object_ref in roots.into_iter().take(limit) {
        if let Ok(proxy) = open_accessible(&conn, &object_ref).await {
            apps.push(read_app_summary(&proxy, &object_ref, dbus.as_ref()).await);
        }
    }

    Ok(apps)
}

pub async fn snapshot_tree(
    app_name_or_bundle_identifier: Option<&str>,
    target_pid: Option<u32>,
    max_nodes: usize,
    max_depth: u32,
) -> Result<Vec<AccessibilityNode>> {
    let (max_nodes, max_depth) = snapshot_limits(Some(max_nodes), Some(max_depth));
    timeout(
        SNAPSHOT_TIMEOUT,
        snapshot_tree_inner(
            app_name_or_bundle_identifier,
            target_pid,
            max_nodes,
            max_depth,
        ),
    )
    .await
    .context("AT-SPI snapshot a dépassé le délai imparti de 10 secondes")?
}

async fn snapshot_tree_inner(
    app_name_or_bundle_identifier: Option<&str>,
    target_pid: Option<u32>,
    max_nodes: usize,
    max_depth: u32,
) -> Result<Vec<AccessibilityNode>> {
    let conn = connect().await?;
    let (mut remaining_registry_reads, mut remaining_filter_reads, mut remaining_traversal_reads) =
        snapshot_child_read_budgets(max_nodes);
    let roots =
        registry_children(&conn, MAX_DISCOVERY_ROOTS, &mut remaining_registry_reads).await?;
    let selected_roots = select_roots(
        &conn,
        roots,
        app_name_or_bundle_identifier,
        target_pid,
        &mut remaining_filter_reads,
    )
    .await;
    let mut nodes = Vec::new();
    let mut traversal = BoundedTraversal::new(max_nodes);

    traversal.enqueue(
        selected_roots
            .into_iter()
            .map(|object_ref| (object_ref, 0_u32, None)),
    );

    while let Some((object_ref, depth, parent_index)) = traversal.pop() {
        let Ok(proxy) = open_accessible(&conn, &object_ref).await else {
            continue;
        };
        let index = nodes.len() as u32;
        let remaining = traversal.remaining_capacity();
        let child_refs = if depth < max_depth && remaining > 0 {
            children_up_to(&proxy, remaining, &mut remaining_traversal_reads)
                .await
                .map(|batch| batch.items)
                .unwrap_or_default()
        } else {
            Vec::new()
        };

        nodes.push(read_node(&proxy, &object_ref, index, parent_index, depth).await);

        traversal.enqueue(
            child_refs
                .into_iter()
                .map(|child| (child, depth + 1, Some(index))),
        );
    }

    Ok(nodes)
}

pub async fn perform_action(
    object_ref_id: &str,
    requested_action: Option<&str>,
) -> Result<ActionInvocation> {
    let conn = connect().await?;
    let object_ref = object_ref_from_id(object_ref_id)?;
    let proxy = open_accessible(&conn, &object_ref)
        .await
        .with_context(|| format!("Impossible d'ouvrir l'objet AT-SPI {object_ref_id}"))?;
    let action = proxy
        .proxies()
        .await?
        .action()
        .await
        .context("Le composant n'implémente pas l'interface AT-SPI Action")?;
    let actions = action.get_actions().await.unwrap_or_default();
    let action_index = select_action_index(&actions, requested_action)?;
    let action_name = actions
        .get(action_index as usize)
        .map(|act| act.name.clone());
    let ok = action
        .do_action(action_index)
        .await
        .with_context(|| format!("Échec d'exécution de l'action AT-SPI index {action_index}"))?;

    Ok(ActionInvocation {
        action_index,
        action_name,
        ok,
    })
}

pub async fn set_element_value(object_ref_id: &str, value: &str) -> Result<ValueSetInvocation> {
    let conn = connect().await?;
    let object_ref = object_ref_from_id(object_ref_id)?;
    let proxy = open_accessible(&conn, &object_ref)
        .await
        .with_context(|| format!("Impossible d'ouvrir l'objet AT-SPI {object_ref_id}"))?;
    let proxies = proxy.proxies().await?;

    if let Ok(numeric_value) = value.parse::<f64>() {
        if let Ok(value_proxy) = proxies.value().await {
            value_proxy
                .set_current_value(numeric_value)
                .await
                .with_context(|| {
                    format!("Échec de modification de la valeur numérique à {numeric_value}")
                })?;
            return Ok(ValueSetInvocation::Numeric {
                value: numeric_value,
            });
        }
    }

    if let Ok(editable_text) = proxies.editable_text().await {
        let ok = editable_text
            .set_text_contents(value)
            .await
            .context("Échec d'écriture directe dans l'interface AT-SPI EditableText")?;
        if ok {
            return Ok(ValueSetInvocation::EditableText);
        }
        return Err(anyhow!("L'interface AT-SPI EditableText a rejeté le contenu"));
    }

    if value.parse::<f64>().is_err() && proxies.value().await.is_ok() {
        return Err(anyhow!(
            "Le composant expose l'interface Value mais la valeur fournie n'est pas numérique"
        ));
    }

    Err(anyhow!(
        "Le composant n'implémente ni l'interface Value ni EditableText"
    ))
}

async fn read_app_summary(
    proxy: &AccessibleProxy<'_>,
    object_ref: &ObjectRefOwned,
    dbus: Option<&DBusProxy<'_>>,
) -> AccessibleAppSummary {
    let name = optional_string(proxy.name().await.ok());
    let role = role_name(proxy).await;
    let child_count = proxy.child_count().await.unwrap_or(0);
    let pid = object_ref_pid(dbus, object_ref).await;
    AccessibleAppSummary {
        object_ref: object_ref_id(object_ref),
        name,
        pid,
        role,
        child_count,
        bounds: bounds(proxy).await,
    }
}

async fn read_node(
    proxy: &AccessibleProxy<'_>,
    object_ref: &ObjectRefOwned,
    index: u32,
    parent_index: Option<u32>,
    depth: u32,
) -> AccessibilityNode {
    let proxies = proxy.proxies().await.ok();
    AccessibilityNode {
        index,
        parent_index,
        depth,
        object_ref: object_ref_id(object_ref),
        role: role_name(proxy).await,
        name: optional_string(proxy.name().await.ok()),
        description: optional_string(proxy.description().await.ok()),
        child_count: proxy.child_count().await.unwrap_or_default(),
        bounds: bounds_from_proxies(proxies.as_ref(), proxy).await,
        states: states_from_proxy(proxy).await,
        actions: actions_from_proxies(proxies.as_ref()).await,
        value: value_from_proxies(proxies.as_ref()).await,
        text: text_from_proxies(proxies.as_ref()).await,
        supports_editable_text: supports_editable_text(proxies.as_ref()).await,
    }
}

async fn role_name(proxy: &AccessibleProxy<'_>) -> String {
    if let Ok(role) = proxy.get_role_name().await {
        if !role.trim().is_empty() {
            return role;
        }
    }
    proxy
        .get_role()
        .await
        .map(|role| format!("{role:?}"))
        .unwrap_or_else(|_| "unknown".to_string())
}

async fn bounds(proxy: &AccessibleProxy<'_>) -> Option<Bounds> {
    bounds_from_proxies(proxy.proxies().await.ok().as_ref(), proxy).await
}

async fn bounds_from_proxies(
    proxies: Option<&atspi::proxy::proxy_ext::Proxies<'_>>,
    proxy: &AccessibleProxy<'_>,
) -> Option<Bounds> {
    let owned_proxies;
    let proxies = if let Some(proxies) = proxies {
        proxies
    } else {
        owned_proxies = proxy.proxies().await.ok()?;
        &owned_proxies
    };
    let component = proxies.component().await.ok()?;
    let (x, y, width, height) = component.get_extents(CoordType::Screen).await.ok()?;
    normalize_bounds(Bounds {
        x,
        y,
        width,
        height,
    })
}

fn normalize_bounds(bounds: Bounds) -> Option<Bounds> {
    if bounds.width <= 0 || bounds.height <= 0 {
        return None;
    }
    if bounds.x <= i32::MIN / 2 || bounds.y <= i32::MIN / 2 {
        return None;
    }
    Some(bounds)
}

async fn actions_from_proxies(
    proxies: Option<&atspi::proxy::proxy_ext::Proxies<'_>>,
) -> Vec<AccessibilityAction> {
    let Some(proxies) = proxies else {
        return Vec::new();
    };
    let Ok(action_proxy) = proxies.action().await else {
        return Vec::new();
    };

    action_proxy
        .get_actions()
        .await
        .unwrap_or_default()
        .into_iter()
        .enumerate()
        .map(|(index, action)| AccessibilityAction {
            index: index as i32,
            name: action.name,
            description: action.description,
            keybinding: action.keybinding,
        })
        .collect()
}

async fn states_from_proxy(proxy: &AccessibleProxy<'_>) -> Vec<String> {
    proxy
        .get_state()
        .await
        .map(state_labels)
        .unwrap_or_default()
}

async fn value_from_proxies(
    proxies: Option<&atspi::proxy::proxy_ext::Proxies<'_>>,
) -> Option<AccessibilityValue> {
    let value = proxies?.value().await.ok()?;
    Some(AccessibilityValue {
        current: value.current_value().await.ok()?,
        minimum: value.minimum_value().await.ok()?,
        maximum: value.maximum_value().await.ok()?,
        minimum_increment: value.minimum_increment().await.ok()?,
        text: optional_string(value.text().await.ok()),
    })
}

async fn text_from_proxies(
    proxies: Option<&atspi::proxy::proxy_ext::Proxies<'_>>,
) -> Option<AccessibilityText> {
    let text = proxies?.text().await.ok()?;
    let character_count = text.character_count().await.ok()?.max(0);
    let caret_offset = text.caret_offset().await.ok();
    let capped_count = character_count.min(MAX_TEXT_READBACK_CHARS);
    let content = if capped_count > 0 {
        optional_string(text.get_text(0, capped_count).await.ok())
    } else {
        None
    };
    let selection_count = text
        .get_nselections()
        .await
        .unwrap_or_default()
        .clamp(0, MAX_TEXT_SELECTIONS);
    let mut selections = Vec::new();
    for index in 0..selection_count {
        if let Ok((start_offset, end_offset)) = text.get_selection(index).await {
            selections.push(AccessibilityTextSelection {
                start_offset,
                end_offset,
            });
        }
    }

    Some(AccessibilityText {
        character_count,
        caret_offset,
        content,
        truncated: character_count > MAX_TEXT_READBACK_CHARS,
        selections,
    })
}

async fn supports_editable_text(proxies: Option<&atspi::proxy::proxy_ext::Proxies<'_>>) -> bool {
    let Some(proxies) = proxies else {
        return false;
    };
    proxies.editable_text().await.is_ok()
}

fn state_labels(state_set: StateSet) -> Vec<String> {
    state_set.iter().map(|state| state.to_string()).collect()
}

fn select_action_index(actions: &[atspi::Action], requested_action: Option<&str>) -> Result<i32> {
    if actions.is_empty() {
        return Err(anyhow!("Le composant n'expose aucune action AT-SPI"));
    }

    if let Some(requested_action) = requested_action
        .map(str::trim)
        .filter(|value| !value.is_empty())
    {
        let requested_action = requested_action.to_ascii_lowercase();
        if let Some((index, _)) = actions.iter().enumerate().find(|(_, action)| {
            action.name.to_ascii_lowercase() == requested_action
                || action.description.to_ascii_lowercase() == requested_action
        }) {
            return Ok(index as i32);
        }

        if let Ok(index) = requested_action.parse::<usize>() {
            if index < actions.len() {
                return Ok(index as i32);
            }
        }

        if matches!(requested_action.as_str(), "activate" | "click" | "press" | "default") {
            return Ok(if actions.len() > 1 { 1 } else { 0 });
        }

        return Err(anyhow!(
            "L'action demandée n'a pas été trouvée ; actions disponibles: {}",
            actions
                .iter()
                .map(|action| action.name.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        ));
    }

    Ok(if actions.len() > 1 { 1 } else { 0 })
}

fn optional_string(value: Option<String>) -> Option<String> {
    value
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
}

pub fn split_object_ref_id(object_ref_id: &str) -> Result<(&str, &str)> {
    let Some(path_start) = object_ref_id.find('/') else {
        return Err(anyhow!(
            "invalid AT-SPI object ref '{object_ref_id}'; expected ':bus/path'"
        ));
    };
    let (name, path) = object_ref_id.split_at(path_start);
    if name.is_empty() || path.is_empty() {
        return Err(anyhow!(
            "invalid AT-SPI object ref '{object_ref_id}'; expected ':bus/path'"
        ));
    }
    Ok((name, path))
}

pub fn object_ref_from_id(object_ref_id: &str) -> Result<ObjectRefOwned> {
    let (name, path) = split_object_ref_id(object_ref_id)?;
    let name = UniqueName::try_from(name.to_string())
        .with_context(|| format!("invalid AT-SPI bus name in object ref {object_ref_id}"))?;
    let path = ObjectPath::try_from(path.to_string())
        .with_context(|| format!("invalid AT-SPI object path in object ref {object_ref_id}"))?;
    Ok(ObjectRef::new_owned(name, path))
}

pub fn object_ref_id(object_ref: &ObjectRefOwned) -> String {
    format!(
        "{}{}",
        object_ref.name_as_str().unwrap_or(""),
        object_ref.path_as_str()
    )
}
