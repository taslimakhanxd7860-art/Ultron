import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
API_KEY = os.environ.get("GEMINI_API_KEY", "")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ULTRON AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#050811;color:#00f6ff;font-family:Arial,sans-serif;text-align:center}
header{padding:20px;border-bottom:1px solid #123b52}
h1{letter-spacing:7px;text-shadow:0 0 20px #00eaff}
.arc{width:150px;height:150px;border-radius:50%;border:3px solid #00f6ff;margin:25px auto;display:flex;align-items:center;justify-content:center;box-shadow:0 0 25px #00dfff,inset 0 0 25px #006080;animation:pulse 2s infinite}
.core{font-size:48px}
@keyframes pulse{50%{box-shadow:0 0 45px #00eaff,inset 0 0 35px #007b99}}
.status{color:#7affb8;font-size:13px}
.panel{margin:14px;padding:16px;border:1px solid #07566a;border-radius:12px;background:#091421}
button{background:#071e2b;color:#00f6ff;border:1px solid #00f6ff;border-radius:9px;padding:12px;margin:5px;width:95%;font-size:15px}
input,textarea{width:95%;padding:12px;border-radius:8px;background:#050811;color:white;border:1px solid #08758b;margin:5px}
#answer{color:white;white-space:pre-wrap;text-align:left;overflow-wrap:anywhere}
small{color:#6d98a8}
</style>
</head>
<body>
<header><h1>ULTRON</h1><div>PERSONAL AI SYSTEM</div></header>
<div class="arc"><div class="core">◉</div></div>
<div class="status">● SYSTEM ONLINE</div>
<div class="panel">
<h3>GEMINI AI COMMAND CENTER</h3>
<textarea id="question" rows="3" placeholder="Ask ULTRON in Hindi or English..."></textarea>
<button onclick="askAI()">✦ ASK GEMINI AI</button>
<button onclick="speakCurrentAnswer()">🔊 SPEAK ANSWER</button>
<textarea id="codingTask" rows="4" placeholder="Write code or explain an error..."></textarea>
<button onclick="askCoding()">ASK ULTRON CODER</button>
<button onclick="listen()">🎙 SPEAK COMMAND</button>
<button onclick="run('time')">🕒 SYSTEM TIME</button>
<button onclick="run('youtube')">▶ OPEN YOUTUBE</button>
<button onclick="run('google')">⌕ WEB SEARCH</button>
<p id="answer">ULTRON ready. Ask me anything.</p>
</div>
<small>ULTRON LUI • MOBILE EDITION</small>
<script>


async function askCoding() {
  const task = document.getElementById("codingTask").value.trim();
  const out = document.getElementById("answer");
  if (!task) { out.innerText = "Pehle coding task likho."; return; }
  out.innerText = "ULTRON Coding Assistant soch raha hai...";
  try {
    const r = await fetch("/code", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({task: task})
    });
    const d = await r.json();
    out.innerText = d.answer || "Koi jawab nahi mila.";
    if (r.ok && d.answer) speakAnswer(d.answer);
  } catch (e) {
    out.innerText = "Connection error. ULTRON server check karo.";
  }
}

function speakAnswer(text) {
  if (!('speechSynthesis' in window)) {
    alert('Voice output is not supported in this browser.');
    return;
  }
  window.speechSynthesis.cancel();
  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = 'hi-IN';
  msg.rate = 1;
  msg.pitch = 1;
  const voices = window.speechSynthesis.getVoices();
  const hindiVoice = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('hi'));
  if (hindiVoice) msg.voice = hindiVoice;
  window.speechSynthesis.speak(msg);
}

function speakCurrentAnswer() {
  speakAnswer(document.getElementById('answer').innerText);
}

async function askAI(){
 const q=document.getElementById('question').value.trim();
 const out=document.getElementById('answer');
 if(!q){out.innerText='Pehle apna sawaal likho ya microphone dabao.';return}
 out.innerText='Gemini AI soch raha hai...';
 try{
  const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  const d=await r.json();
  out.innerText=d.answer||d.error||'Koi jawab nahi mila.';
  if (r.ok && d.answer) speakAnswer(d.answer);
 }catch(e){out.innerText='Connection error. Check Termux server and internet.'}
}
function run(cmd){
 if(cmd==='time')document.getElementById('answer').innerText='Local time: '+new Date().toLocaleTimeString();
 if(cmd==='youtube')location.href='https://m.youtube.com';
 if(cmd==='google')location.href='https://www.google.com';
}
function listen(){
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!SR){document.getElementById('answer').innerText='Voice recognition unavailable. Try Chrome.';return}
 const r=new SR();r.lang='hi-IN';
 r.onresult=function(e){
  const q=e.results[0][0].transcript;
  document.getElementById('question').value=q;
  if(q.toLowerCase().includes('youtube'))run('youtube');
  else if(q.toLowerCase().includes('google')||q.toLowerCase().includes('search'))run('google');
  else if(q.toLowerCase().includes('time')||q.includes('समय'))run('time');
  else askAI();
 };
 r.onerror=function(){document.getElementById('answer').innerText='Voice error. Check microphone permission.'};
 r.start();
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    if not API_KEY:
        return jsonify(answer="Gemini API key is not set. Stop server and set GEMINI_API_KEY again."), 500
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    if not question:
        return jsonify(answer="Please enter a question."), 400
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
            headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": question}]}]},
            timeout=60
        )
        if not response.ok:
            return jsonify(answer="Gemini API error (" + str(response.status_code) + "). Check API key, model access, and quota."), 502
        result = response.json()
        answer = "".join(
            part.get("text", "")
            for candidate in result.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        ).strip()
        return jsonify(answer=answer or "Gemini returned no text.")
    except requests.RequestException:
        return jsonify(answer="Internet or Gemini connection error. Try again."), 502


@app.route("/code", methods=["POST"])
def coding_assistant():
    if not API_KEY:
        return jsonify(answer="Gemini API key is missing."), 500

    data = request.get_json(silent=True) or {}
    task = str(data.get("task", "")).strip()
    if not task:
        return jsonify(answer="Please describe the coding task."), 400

    prompt = (
        "You are ULTRON Coding Assistant, an expert programming tutor. "
        "Help with writing code, debugging, explaining errors, and Android development. "
        "Reply in the user's language, preferably Hindi/Hinglish when appropriate. "
        "Give practical code and clear steps. Never claim code was executed unless it was.\n\n"
        "User coding task:\n" + task
    )

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
            headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
        )
        if not response.ok:
            return jsonify(answer="Gemini API error (" + str(response.status_code) + "). Check API key, model access, and quota."), 502

        result = response.json()
        answer = "".join(
            part.get("text", "")
            for candidate in result.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        ).strip()
        return jsonify(answer=answer or "Gemini returned no text.")
    except requests.RequestException:
        return jsonify(answer="Internet or Gemini connection error. Try again."), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
