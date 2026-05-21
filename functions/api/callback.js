/**
 * Cloudflare Pages Function — GitHub OAuth callback
 * GET /api/callback?code=xxx
 * Sveltia/Decap CMS opener penceresine token mesajı gönderir
 */
export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const code = url.searchParams.get('code');

  if (!code) {
    return errorPage('No authorization code received');
  }

  const clientId = context.env.GITHUB_CLIENT_ID;
  const clientSecret = context.env.GITHUB_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    return errorPage('OAuth env vars missing on server');
  }

  // GitHub'dan access token al
  const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      redirect_uri: `${url.origin}/api/callback`,
    }),
  });

  const data = await tokenRes.json();

  if (data.error || !data.access_token) {
    return errorPage(`GitHub error: ${data.error_description || data.error}`);
  }

  // Sveltia/Decap CMS'in beklediği mesaj formatı
  const token = data.access_token;
  const message = `authorization:github:success:${JSON.stringify({
    token,
    provider: 'github',
  })}`;

  return new Response(
    `<!DOCTYPE html>
<html>
<body>
<script>
(function () {
  var message = ${JSON.stringify(message)};
  function receiveMessage(e) {
    window.opener.postMessage(message, e.origin);
    window.removeEventListener('message', receiveMessage, false);
    window.close();
  }
  window.addEventListener('message', receiveMessage, false);
  window.opener.postMessage('authorizing:github', '*');
})();
</script>
</body>
</html>`,
    { headers: { 'Content-Type': 'text/html;charset=UTF-8' } }
  );
}

function errorPage(msg) {
  const message = `authorization:github:error:${JSON.stringify({ message: msg })}`;
  return new Response(
    `<!DOCTYPE html>
<html>
<body>
<script>
(function () {
  var message = ${JSON.stringify(message)};
  window.opener && window.opener.postMessage(message, '*');
  window.close();
})();
</script>
<p style="font-family:sans-serif;color:red">${msg}</p>
</body>
</html>`,
    { status: 400, headers: { 'Content-Type': 'text/html;charset=UTF-8' } }
  );
}
