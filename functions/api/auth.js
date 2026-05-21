/**
 * Cloudflare Pages Function — GitHub OAuth başlangıç noktası
 * GET /api/auth?provider=github
 * Sveltia/Decap CMS'in base_url + auth_endpoint ile çağırdığı endpoint
 */
export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const provider = url.searchParams.get('provider');

  if (provider !== 'github') {
    return new Response('Unsupported provider', { status: 400 });
  }

  const clientId = context.env.GITHUB_CLIENT_ID;
  if (!clientId) {
    return new Response('GITHUB_CLIENT_ID env var missing', { status: 500 });
  }

  const redirectUri = `${url.origin}/api/callback`;
  const scope = 'repo,user';

  const githubUrl =
    `https://github.com/login/oauth/authorize` +
    `?client_id=${encodeURIComponent(clientId)}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&scope=${encodeURIComponent(scope)}` +
    `&response_type=code`;

  return Response.redirect(githubUrl, 302);
}
