# email_service.py - Envio de correos SMTP para el panel admin
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


def smtp_configurado():
    return bool(Config.SMTP_HOST and Config.SMTP_USER and Config.SMTP_PASSWORD)


def enviar_correo(destinatario, asunto, mensaje_html, remitente_nombre=None):
    if not smtp_configurado():
        raise RuntimeError("SMTP no configurado: defina SMTP_HOST, SMTP_USER y SMTP_PASSWORD")
    remitente = (Config.EMAIL_FROM or Config.SMTP_USER).strip()
    nombre = (remitente_nombre or Config.EMAIL_FROM_NAME or remitente).strip()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = f"{nombre} <{remitente}>"
    msg["To"] = destinatario
    msg.attach(MIMEText(mensaje_html, "html", "utf-8"))

    port = Config.SMTP_PORT
    context = ssl.create_default_context()

    if port == 465:
        with smtplib.SMTP_SSL(Config.SMTP_HOST, port, context=context, timeout=30) as server:
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(remitente, [destinatario], msg.as_string())
    else:
        with smtplib.SMTP(Config.SMTP_HOST, port, timeout=30) as server:
            server.ehlo()
            if Config.SMTP_STARTTLS:
                server.starttls(context=context)
                server.ehlo()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(remitente, [destinatario], msg.as_string())


def plantilla_correo(nombre_destinatario, cuerpo):
    nombre_html = nombre_destinatario.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cuerpo_html = cuerpo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    return f"""\
<html>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px;">
    <div style="background:#00b689;border-radius:12px 12px 0 0;padding:20px 24px;">
      <h2 style="color:#ffffff;margin:0;font-size:20px;">{Config.EMAIL_FROM_NAME}</h2>
    </div>
    <div style="background:#ffffff;border-radius:0 0 12px 12px;padding:28px 24px;color:#2d3436;line-height:1.6;">
      <p>Estimado/a <strong>{nombre_html}</strong>:</p>
      <div style="margin:16px 0;">{cuerpo_html}</div>
      <p>Atentamente,<br><strong>{Config.EMAIL_FROM_NAME}</strong></p>
    </div>
    <p style="text-align:center;color:#98a2b3;font-size:12px;margin-top:16px;">
      Mensaje enviado desde el Sistema Escolar INSCRIBE.
    </p>
  </div>
</body>
</html>"""
