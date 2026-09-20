/**
 * Cloudflare Pages Function â€” POST /api/contact
 * Runtime : Cloudflare Workers (edge)
 * Email   : Resend API (fetch natif, pas de SDK Ã  bundler)
 * Destinataires : cblniv15@gmail.com Â· infoProf. Thioune@gmail.com
 */

export async function onRequestPost(context) {
  const { request, env } = context;

  // --- Parse body ---
  let body;
  try {
    const contentType = request.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      body = await request.json();
    } else {
      const fd = await request.formData();
      body = Object.fromEntries(
        Array.from(fd.entries()).map(([k, v]) => [k, v.toString()])
      );
    }
  } catch {
    return Response.json(
      { success: false, error: "RequÃªte invalide." },
      { status: 400 }
    );
  }

  const { firstName, lastName, email, subject, message } = body ?? {};

  // --- Validation ---
  if (
    !firstName?.trim() ||
    !lastName?.trim() ||
    !email?.trim() ||
    !message?.trim()
  ) {
    return Response.json(
      { success: false, error: "Tous les champs obligatoires doivent Ãªtre remplis." },
      { status: 400 }
    );
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return Response.json(
      { success: false, error: "Adresse email invalide." },
      { status: 400 }
    );
  }

  // --- ClÃ© API Web3Forms ---
  const accessKey = env.WEB3FORMS_ACCESS_KEY || "14e39eb2-cb9b-4792-acd2-b199a8272685";

  if (!accessKey || accessKey.startsWith("PLACEHOLDER")) {
    return Response.json(
      { success: false, error: "Configuration email (Web3Forms) manquante." },
      { status: 500 }
    );
  }

  // --- Envoi via Web3Forms API ---
  try {
    const web3formsPayload = {
      access_key: accessKey,
      name: `${firstName} ${lastName}`,
      email: email,
      subject: subject?.trim() ? `[Prof. Thioune] ${subject.trim()}` : "Nouveau message depuis Prof. Thioune",
      message: message,
      replyto: email
    };

    const response = await fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(web3formsPayload),
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      console.error("[Web3Forms Error]", response.status, result);
      return Response.json(
        { success: false, error: "Erreur lors de l'envoi. Veuillez rÃ©essayer." },
        { status: 500 }
      );
    }

    return Response.json({ success: true }, { status: 200 });
  } catch (e) {
    console.error("[Contact Function Error]", e);
    return Response.json(
      { success: false, error: "Erreur serveur. Veuillez rÃ©essayer." },
      { status: 500 }
    );
  }
}


