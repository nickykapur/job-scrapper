import React, { useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { FileText, Mail, Phone, MapPin, Linkedin, Github, Link, RefreshCw } from 'lucide-react';
import { jobApi } from '../services/api';

interface CVUpload {
  id: number;
  user_id: number;
  username: string;
  user_email: string;
  user_full_name?: string | null;
  is_admin: boolean;
  is_active: boolean;
  full_name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  skills: string[];
  skills_count: number;
  summary?: string | null;
  cv_filename?: string | null;
  uploaded_at?: string | null;
  updated_at?: string | null;
}

function fmtDate(iso?: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString(undefined, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export const AdminCVUploads: React.FC = () => {
  const [items, setItems] = useState<CVUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<CVUpload | null>(null);
  const [query, setQuery] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await jobApi.adminListCVUploads();
      setItems(res.items || []);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to load CV uploads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter(i =>
      (i.username || '').toLowerCase().includes(q) ||
      (i.user_email || '').toLowerCase().includes(q) ||
      (i.user_full_name || '').toLowerCase().includes(q) ||
      (i.cv_filename || '').toLowerCase().includes(q) ||
      (i.skills || []).some(s => s.toLowerCase().includes(q))
    );
  }, [items, query]);

  return (
    <div style={{ padding: 20, color: '#e5e7eb' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>CV Uploads</h2>
          <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#9ca3af' }}>
            {items.length} users have uploaded a CV
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search user, filename, skill…"
            style={{
              background: '#1f2937', border: '1px solid #374151', borderRadius: 6,
              color: '#e5e7eb', padding: '8px 12px', fontSize: 13, minWidth: 240,
            }}
          />
          <button
            onClick={load}
            disabled={loading}
            style={{
              background: '#374151', border: 'none', borderRadius: 6,
              color: '#e5e7eb', padding: '8px 14px', fontSize: 13, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 6,
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {loading && items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Loading…</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>No CV uploads yet.</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 1fr' : '1fr', gap: 16 }}>
          <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 8, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: '#1f2937', color: '#9ca3af', textAlign: 'left' }}>
                  <th style={{ padding: 10 }}>User</th>
                  <th style={{ padding: 10 }}>File</th>
                  <th style={{ padding: 10 }}>Skills</th>
                  <th style={{ padding: 10 }}>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => (
                  <tr
                    key={u.id}
                    onClick={() => setSelected(u)}
                    style={{
                      cursor: 'pointer',
                      borderTop: '1px solid #1f2937',
                      background: selected?.id === u.id ? '#1e293b' : 'transparent',
                    }}
                  >
                    <td style={{ padding: 10 }}>
                      <div style={{ fontWeight: 600 }}>{u.user_full_name || u.username}</div>
                      <div style={{ fontSize: 11, color: '#9ca3af' }}>{u.user_email}</div>
                    </td>
                    <td style={{ padding: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <FileText size={14} color="#60a5fa" />
                        <span style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {u.cv_filename || '—'}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: 10 }}>
                      <span style={{ background: '#064e3b', color: '#6ee7b7', padding: '2px 8px', borderRadius: 10, fontSize: 11 }}>
                        {u.skills_count}
                      </span>
                    </td>
                    <td style={{ padding: 10, color: '#9ca3af' }}>{fmtDate(u.updated_at || u.uploaded_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selected && (
            <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 8, padding: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 600 }}>{selected.user_full_name || selected.username}</div>
                  <div style={{ fontSize: 12, color: '#9ca3af' }}>@{selected.username} · {selected.user_email}</div>
                </div>
                <button
                  onClick={() => setSelected(null)}
                  style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: 18 }}
                >×</button>
              </div>

              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
                <span style={{ background: '#1e3a8a', color: '#bfdbfe', padding: '2px 8px', borderRadius: 10, fontSize: 11 }}>
                  {selected.cv_filename || 'no file'}
                </span>
                <span style={{ background: '#064e3b', color: '#6ee7b7', padding: '2px 8px', borderRadius: 10, fontSize: 11 }}>
                  {selected.skills_count} skills
                </span>
                {selected.is_admin && (
                  <span style={{ background: '#7c2d12', color: '#fed7aa', padding: '2px 8px', borderRadius: 10, fontSize: 11 }}>
                    admin
                  </span>
                )}
                {!selected.is_active && (
                  <span style={{ background: '#4c1d95', color: '#e9d5ff', padding: '2px 8px', borderRadius: 10, fontSize: 11 }}>
                    inactive
                  </span>
                )}
              </div>

              <section style={{ marginBottom: 14 }}>
                <h4 style={{ fontSize: 12, color: '#9ca3af', margin: '0 0 6px 0', textTransform: 'uppercase', letterSpacing: 1 }}>Contact</h4>
                <div style={{ display: 'grid', gap: 4, fontSize: 13 }}>
                  {selected.email && <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Mail size={12} />{selected.email}</div>}
                  {selected.phone && <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Phone size={12} />{selected.phone}</div>}
                  {selected.location && <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><MapPin size={12} />{selected.location}</div>}
                  {selected.linkedin_url && <a href={selected.linkedin_url} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', display: 'flex', alignItems: 'center', gap: 6 }}><Linkedin size={12} />LinkedIn</a>}
                  {selected.github_url && <a href={selected.github_url} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', display: 'flex', alignItems: 'center', gap: 6 }}><Github size={12} />GitHub</a>}
                  {selected.portfolio_url && <a href={selected.portfolio_url} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', display: 'flex', alignItems: 'center', gap: 6 }}><Link size={12} />Portfolio</a>}
                </div>
              </section>

              {selected.summary && (
                <section style={{ marginBottom: 14 }}>
                  <h4 style={{ fontSize: 12, color: '#9ca3af', margin: '0 0 6px 0', textTransform: 'uppercase', letterSpacing: 1 }}>Summary</h4>
                  <p style={{ margin: 0, fontSize: 13, lineHeight: 1.5, color: '#d1d5db' }}>{selected.summary}</p>
                </section>
              )}

              {selected.skills?.length > 0 && (
                <section style={{ marginBottom: 14 }}>
                  <h4 style={{ fontSize: 12, color: '#9ca3af', margin: '0 0 6px 0', textTransform: 'uppercase', letterSpacing: 1 }}>Skills ({selected.skills.length})</h4>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {selected.skills.map((s, i) => (
                      <span key={i} style={{ background: '#1f2937', color: '#d1d5db', padding: '3px 8px', borderRadius: 4, fontSize: 11 }}>{s}</span>
                    ))}
                  </div>
                </section>
              )}

              <div style={{ borderTop: '1px solid #1f2937', paddingTop: 10, marginTop: 12, fontSize: 11, color: '#6b7280' }}>
                <div>Uploaded: {fmtDate(selected.uploaded_at)}</div>
                <div>Updated: {fmtDate(selected.updated_at)}</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminCVUploads;
