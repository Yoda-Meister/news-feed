import { useEffect, useRef } from 'react'

const WIDGETS_SCRIPT_URL = 'https://platform.twitter.com/widgets.js'

export default function TwitterFeed({ listUrl }) {
  const scriptLoaded = useRef(false)

  useEffect(() => {
    if (scriptLoaded.current) return
    scriptLoaded.current = true

    if (window.twttr) {
      window.twttr.widgets.load()
      return
    }

    const script = document.createElement('script')
    script.src = WIDGETS_SCRIPT_URL
    script.async = true
    script.charset = 'utf-8'
    document.body.appendChild(script)
  }, [])

  if (!listUrl || listUrl.includes('YOUR_LIST_ID')) {
    return (
      <div className="twitter-feed">
        <div className="feed-header">
          <h1>Twitter / X</h1>
        </div>
        <p className="feed-placeholder">
          Set your Twitter List URL in <code>config.json</code> to enable this feed.
        </p>
      </div>
    )
  }

  return (
    <div className="twitter-feed">
      <div className="feed-header">
        <h1>Twitter / X</h1>
      </div>
      <a
        className="twitter-timeline"
        data-theme="light"
        data-chrome="noheader nofooter"
        data-tweet-limit="20"
        href={listUrl}
      >
        Loading tweets…
      </a>
    </div>
  )
}
