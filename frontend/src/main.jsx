import { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "/api";
const CHUNK_SIZE = 5 * 1024 * 1024;

async function api(path, token, options = {}) {
  const headers = new Headers(options.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the status-based message for non-JSON proxy errors.
    }
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}

function formatBytes(value) {
  if (value === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(value) / Math.log(1024)), units.length - 1);
  return `${(value / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "register") {
        await api("/auth/register", null, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
      }
      const form = new URLSearchParams({ username: email, password });
      const result = await api("/auth/login", null, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
      onLogin(result.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand-mark">F</div>
        <p className="eyebrow">PRIVATE CLOUD STORAGE</p>
        <h1>{mode === "login" ? "Welcome back" : "Create your account"}</h1>
        <p className="muted">Your files, secure and accessible from anywhere.</p>
        <form onSubmit={submit} className="form-stack">
          <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label>Password<input type="password" minLength="8" autoComplete={mode === "login" ? "current-password" : "new-password"} required value={password} onChange={(e) => setPassword(e.target.value)} /></label>
          {error && <div className="alert">{error}</div>}
          <button className="button primary full" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}</button>
        </form>
        <p className="switch-auth">
          {mode === "login" ? "New to FileVault?" : "Already have an account?"}{" "}
          <button className="text-button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
            {mode === "login" ? "Create account" : "Sign in"}
          </button>
        </p>
      </section>
    </main>
  );
}

function Dashboard({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [pageData, setPageData] = useState({ page: 1, total: 0, total_pages: 0 });
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [shareFile, setShareFile] = useState(null);
  const [shares, setShares] = useState([]);
  const [shareUrl, setShareUrl] = useState("");
  const [shareHours, setShareHours] = useState(24);
  const [maxDownloads, setMaxDownloads] = useState("");
  const [shareBusy, setShareBusy] = useState(false);
  const [dragging, setDragging] = useState(false);

  const initials = useMemo(() => (user?.email || "F").slice(0, 1).toUpperCase(), [user]);

  async function loadFiles(targetPage = page, query = search) {
    setError("");
    try {
      const params = new URLSearchParams({
        page: String(targetPage),
        page_size: "10",
        sort_by: sortBy,
        sort_order: "desc",
      });
      if (query) params.set("search", query);
      const result = await api(`/files/?${params}`, token);
      setFiles(result.items);
      setPageData(result);
      setPage(result.page);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    api("/auth/me", token).then(setUser).catch(() => onLogout());
  }, [token]);

  useEffect(() => {
    loadFiles(1, search);
  }, [search, sortBy]);

  async function uploadFiles(selected) {
    if (!selected?.length) return;
    setBusy(true);
    setError("");
    let completed = 0;
    const totalBytes = [...selected].reduce((sum, file) => sum + file.size, 0);
    try {
      for (const file of selected) {
        const chunks = Math.max(1, Math.ceil(file.size / CHUNK_SIZE));
        const session = await api("/uploads/initiate", token, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: file.name, total_chunks: chunks }),
        });
        for (let index = 0; index < chunks; index += 1) {
          const form = new FormData();
          form.append("file", file.slice(index * CHUNK_SIZE, (index + 1) * CHUNK_SIZE), file.name);
          await api(`/uploads/${session.upload_id}/chunks/${index + 1}`, token, { method: "POST", body: form });
          completed += file.size === 0 ? 0 : Math.min(CHUNK_SIZE, file.size - index * CHUNK_SIZE);
          setProgress(totalBytes ? Math.round((completed / totalBytes) * 100) : 100);
        }
        await api(`/uploads/${session.upload_id}/complete`, token, { method: "POST" });
      }
      await loadFiles(1, search);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      setProgress(null);
    }
  }

  async function download(file) {
    try {
      const result = await api(`/files/${file.id}/download`, token);
      window.location.assign(result.url);
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(file) {
    if (!window.confirm(`Delete "${file.filename}"? This cannot be undone.`)) return;
    try {
      await api(`/files/${file.id}`, token, { method: "DELETE" });
      await loadFiles(page, search);
    } catch (err) {
      setError(err.message);
    }
  }

  async function openShares(file) {
    setShareFile(file);
    setShareUrl("");
    try {
      setShares(await api(`/files/${file.id}/shares`, token));
    } catch (err) {
      setError(err.message);
    }
  }

  async function createShare(event) {
    event.preventDefault();
    setShareBusy(true);
    try {
      const result = await api(`/files/${shareFile.id}/share`, token, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expires_in_hours: Number(shareHours),
          max_downloads: maxDownloads ? Number(maxDownloads) : null,
        }),
      });
      setShareUrl(result.share_url);
      setShares(await api(`/files/${shareFile.id}/shares`, token));
    } catch (err) {
      setError(err.message);
    } finally {
      setShareBusy(false);
    }
  }

  async function revokeShare(shareId) {
    try {
      await api(`/files/${shareFile.id}/share/${shareId}`, token, { method: "DELETE" });
      setShares(await api(`/files/${shareFile.id}/shares`, token));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#"><span className="brand-mark small">F</span><span>FileVault</span></a>
        <div className="user-menu">
          <span className="avatar">{initials}</span>
          <span className="user-email">{user?.email || "Loading account…"}</span>
          <button className="button quiet" onClick={onLogout}>Sign out</button>
        </div>
      </header>

      <section className="content">
        <div className="page-heading">
          <div><p className="eyebrow">YOUR WORKSPACE</p><h1>My files</h1><p className="muted">Keep everything important in one secure place.</p></div>
          <label className={`button primary upload-button ${busy ? "disabled" : ""}`}>
            <input type="file" multiple disabled={busy} onChange={(event) => { uploadFiles(event.target.files); event.target.value = ""; }} />
            <span aria-hidden="true">＋</span> Upload files
          </label>
        </div>

        <section
          className={`upload-panel ${dragging ? "dragging" : ""}`}
          onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
          onDragLeave={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setDragging(false); }}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            uploadFiles(event.dataTransfer.files);
          }}
        >
          <div className="upload-icon" aria-hidden="true">↑</div>
          <div><strong>{busy ? "Uploading your files…" : "Add files to your vault"}</strong><p className="muted">Large files are sent sequentially in secure 5 MB chunks. Select one or more files to begin.</p></div>
          {busy && <span className="progress-label">{progress ?? 0}%</span>}
          {busy && <div className="progress-track"><span style={{ width: `${progress ?? 0}%` }} /></div>}
        </section>

        {error && <div className="alert page-alert" role="alert">{error}<button onClick={() => setError("")} aria-label="Dismiss">×</button></div>}
        <section className="file-section">
          <div className="section-heading">
            <div><h2>Files <span className="count">{pageData.total}</span></h2><p className="muted">Manage your stored files and share links.</p></div>
            <div className="file-tools">
              <form className="search" onSubmit={(event) => { event.preventDefault(); setSearch(searchInput.trim()); }}>
                <span aria-hidden="true">⌕</span><input aria-label="Search by filename" placeholder="Search files" value={searchInput} onChange={(event) => setSearchInput(event.target.value)} />
                {searchInput && <button type="button" className="clear-search" onClick={() => { setSearchInput(""); setSearch(""); }}>×</button>}
              </form>
              <label className="sort-select"><span className="sr-only">Sort files</span><select value={sortBy} onChange={(event) => setSortBy(event.target.value)}><option value="created_at">Newest</option><option value="filename">Name</option><option value="size">Size</option></select></label>
            </div>
          </div>
          <div className="file-table">
            <div className="table-head"><span>Name</span><span>Size</span><span>Added</span><span>Actions</span></div>
            {files.map((file) => (
              <div className="file-row" key={file.id}>
                <div className="file-name"><span className="file-icon">▧</span><span title={file.filename}>{file.filename}</span></div>
                <span className="file-size">{formatBytes(file.size)}</span>
                <span className="file-date">{new Date(file.created_at).toLocaleDateString()}</span>
                <div className="file-actions">
                  <button className="icon-button" title="Download" aria-label={`Download ${file.filename}`} onClick={() => download(file)}>↓</button>
                  <button className="icon-button" title="Share" aria-label={`Share ${file.filename}`} onClick={() => openShares(file)}>↗</button>
                  <button className="icon-button danger" title="Delete" aria-label={`Delete ${file.filename}`} onClick={() => remove(file)}>×</button>
                </div>
              </div>
            ))}
            {!files.length && <div className="empty-state"><span>▧</span><strong>{search ? "No matching files" : "Your vault is empty"}</strong><p className="muted">{search ? "Try another filename." : "Upload your first file to get started."}</p></div>}
          </div>
          <div className="pagination">
            <span className="muted">{pageData.total ? `Showing ${(page - 1) * 10 + 1}–${Math.min(page * 10, pageData.total)} of ${pageData.total}` : "No files"}</span>
            <div><button className="button quiet" disabled={page <= 1} onClick={() => loadFiles(page - 1)}>Previous</button><button className="button quiet" disabled={page >= pageData.total_pages} onClick={() => loadFiles(page + 1)}>Next</button></div>
          </div>
        </section>
        <footer className="footer"><span>FileVault</span><span>Private storage, built for you.</span></footer>
      </section>

      {shareFile && <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setShareFile(null); }}>
        <section className="modal" role="dialog" aria-modal="true" aria-labelledby="share-title">
          <button className="modal-close" onClick={() => setShareFile(null)} aria-label="Close">×</button>
          <p className="eyebrow">PUBLIC LINK</p><h2 id="share-title">Share {shareFile.filename}</h2><p className="muted">Anyone with this link can download the file until it expires or is revoked.</p>
          <form onSubmit={createShare} className="share-form">
            <label>Expires in<select value={shareHours} onChange={(e) => setShareHours(e.target.value)}><option value="1">1 hour</option><option value="24">24 hours</option><option value="168">7 days</option><option value="720">30 days</option></select></label>
            <label>Maximum downloads <input type="number" min="1" max="10000" placeholder="Unlimited" value={maxDownloads} onChange={(e) => setMaxDownloads(e.target.value)} /></label>
            <button className="button primary full" disabled={shareBusy}>{shareBusy ? "Creating link…" : "Create share link"}</button>
          </form>
          {shareUrl && <div className="new-share"><label>Link (shown only now)<input readOnly value={shareUrl} onFocus={(e) => e.target.select()} /></label><button className="button secondary" onClick={() => navigator.clipboard.writeText(shareUrl)}>Copy link</button></div>}
          <div className="existing-shares"><h3>Existing links</h3>
            {!shares.length && <p className="muted small-text">No share links yet.</p>}
            {shares.map((share) => <div className="share-row" key={share.id}>
              <div><strong>{share.revoked ? "Revoked" : "Active link"}</strong><span>{share.download_count}{share.max_downloads ? ` / ${share.max_downloads}` : ""} downloads · expires {new Date(share.expires_at).toLocaleString()}</span></div>
              {!share.revoked && <button className="text-button danger-text" onClick={() => revokeShare(share.id)}>Revoke</button>}
            </div>)}
          </div>
          <p className="share-note">For security, full link tokens are never stored; the link can only be copied when it is first created.</p>
        </section>
      </div>}
    </main>
  );
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("filevault-token"));
  function login(value) {
    localStorage.setItem("filevault-token", value);
    setToken(value);
  }
  function logout() {
    localStorage.removeItem("filevault-token");
    setToken(null);
  }
  return token ? <Dashboard token={token} onLogout={logout} /> : <AuthScreen onLogin={login} />;
}

createRoot(document.getElementById("root")).render(<App />);
