import { useState, useEffect, useRef } from 'react'

const INITIAL_VISIBLE = 3
const LOAD_MORE_STEP = 3
const EMBED_SCRIPT_URL = '//www.instagram.com/embed.js'

function processEmbeds() {
  if (window.instgrm && window.instgrm.Embeds) {
    window.instgrm.Embeds.process()
  }
}

function AccountSection({ username, posts }) {
  const [visible, setVisible] = useState(INITIAL_VISIBLE)

  // Re-process embeds whenever the visible slice changes
  useEffect(() => {
    processEmbeds()
  }, [visible])

  const visiblePosts = posts.slice(0, visible)
  const hasMore = visible < posts.length

  return (
    <section className="account-section">
      <h2 className="account-title">
        <a
          href={`https://www.instagram.com/${username}/`}
          target="_blank"
          rel="noopener noreferrer"
        >
          @{username}
        </a>
      </h2>

      <div className="posts-grid">
        {visiblePosts.map((post) => (
          <blockquote
            key={post.shortcode}
            className="instagram-media"
            data-instgrm-captioned
            data-instgrm-permalink={post.post_url}
            data-instgrm-version="14"
            style={{
              background: '#FFF',
              border: '0',
              borderRadius: '3px',
              boxShadow: '0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,0.15)',
              margin: '1px',
              maxWidth: '540px',
              minWidth: '326px',
              padding: '0',
              width: '100%',
            }}
          >
            <div style={{ padding: '16px' }}>
              <a
                href={post.post_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#000', fontFamily: 'Arial, sans-serif', fontSize: '14px', fontStyle: 'normal', fontWeight: 'normal', lineHeight: '17px', textDecoration: 'none', wordBreak: 'break-all' }}
              >
                View this post on Instagram
              </a>
            </div>
          </blockquote>
        ))}
      </div>

      {hasMore && (
        <button
          className="load-more-btn"
          onClick={() => setVisible((v) => Math.min(v + LOAD_MORE_STEP, posts.length))}
        >
          Load 3 more from @{username}
        </button>
      )}
    </section>
  )
}

export default function InstagramFeed({ data }) {
  const scriptLoaded = useRef(false)

  // Load the Instagram embed script once
  useEffect(() => {
    if (scriptLoaded.current) return
    scriptLoaded.current = true

    const script = document.createElement('script')
    script.src = EMBED_SCRIPT_URL
    script.async = true
    script.defer = true
    document.body.appendChild(script)
  }, [])

  if (!data) {
    return <p className="feed-placeholder">Loading Instagram posts…</p>
  }

  const { accounts, last_updated } = data
  const accountNames = Object.keys(accounts)

  if (accountNames.length === 0) {
    return <p className="feed-placeholder">No Instagram posts yet. Check back soon.</p>
  }

  return (
    <div className="instagram-feed">
      <div className="feed-header">
        <h1>Instagram</h1>
        {last_updated && (
          <span className="last-updated">
            Updated {new Date(last_updated).toLocaleString()}
          </span>
        )}
      </div>

      {accountNames.map((username) => (
        <AccountSection
          key={username}
          username={username}
          posts={accounts[username]}
        />
      ))}
    </div>
  )
}
