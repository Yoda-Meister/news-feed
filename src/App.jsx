import { useState, useEffect } from 'react'
import InstagramFeed from './components/InstagramFeed'
import TwitterFeed from './components/TwitterFeed'
import './App.css'

function App() {
  const [igData, setIgData] = useState(null)
  const [twitterListUrl, setTwitterListUrl] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Load instagram data
    fetch('./data/instagram.json')
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load instagram.json: ${r.status}`)
        return r.json()
      })
      .then(setIgData)
      .catch((e) => setError(e.message))

    // Load config for twitter list URL
    fetch('./config.json')
      .then((r) => r.json())
      .then((cfg) => setTwitterListUrl(cfg.twitter_list_url))
      .catch(() => {}) // non-fatal
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>My Newsfeed</h1>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <main className="feeds-layout">
        <section className="feed-column">
          <InstagramFeed data={igData} />
        </section>
        <section className="feed-column">
          <TwitterFeed listUrl={twitterListUrl} />
        </section>
      </main>
    </div>
  )
}

export default App
