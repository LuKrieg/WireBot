const DEFAULT_ERROR_MESSAGE = 'Ocurrió un problema con el servidor.'

/** Tras reinicio del backend o contenedor Docker el proxy puede devolver 502/503 unos segundos. */
const TRANSIENT_STATUSES = new Set([502, 503, 504])

function buildHeaders(headers = {}) {
  return {
    'Content-Type': 'application/json',
    ...headers,
  }
}

function parseBody(text) {
  if (!text) return {}

  try {
    return JSON.parse(text)
  } catch {
    return { error: text }
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function apiRequest(path, options = {}) {
  const maxAttempts = 12
  const baseDelayMs = 400
  let last = null

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await fetch(path, {
        ...options,
        headers: buildHeaders(options.headers),
      })

      const rawText = await response.text()
      const data = parseBody(rawText)
      last = {
        ok: response.ok,
        status: response.status,
        data,
        errorMessage: data.error || DEFAULT_ERROR_MESSAGE,
      }

      if (response.ok || !TRANSIENT_STATUSES.has(response.status)) {
        return last
      }
    } catch {
      last = {
        ok: false,
        status: 0,
        data: {},
        errorMessage: DEFAULT_ERROR_MESSAGE,
      }
    }

    if (attempt < maxAttempts - 1) {
      await sleep(baseDelayMs * (attempt + 1))
    }
  }

  return (
    last || {
      ok: false,
      status: 0,
      data: {},
      errorMessage: DEFAULT_ERROR_MESSAGE,
    }
  )
}
