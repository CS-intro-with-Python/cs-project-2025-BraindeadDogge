import { Buffer } from 'node:buffer'

export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const username = config.basicAuthUser
  const password = config.basicAuthPassword

  // Disable auth when credentials are not configured.
  if (!username || !password) {
    return
  }

  const header = getHeader(event, 'authorization')
  const prefix = 'Basic '

  if (!header || !header.startsWith(prefix)) {
    setHeader(event, 'www-authenticate', 'Basic realm="Restricted"')
    throw createError({ statusCode: 401, statusMessage: 'Authentication required' })
  }

  const decoded = Buffer.from(header.slice(prefix.length), 'base64').toString('utf-8')
  const [providedUser, providedPass = ''] = decoded.split(':')

  if (providedUser !== username || providedPass !== password) {
    setHeader(event, 'www-authenticate', 'Basic realm="Restricted"')
    throw createError({ statusCode: 401, statusMessage: 'Invalid credentials' })
  }
})
