// The King Lives — Daily Production Script
// Paste this into script.google.com → New project
// Then: Project Settings → Script Properties → add OPENROUTER_API_KEY
// Then: Triggers → Add trigger → runDaily → Time-driven → Day timer → 8am

var TOPICS = [
  "The night Elvis walked into Sun Studio and accidentally invented rock and roll — July 5, 1954",
  "Elvis and his mother Gladys — the bond that built him and the loss that broke him",
  "The day Elvis met Nixon and asked to become a federal drug agent",
  "Elvis's final performance of Unchained Melody — Rapid City, June 21, 1977",
  "The night Elvis was so nervous about his first radio play he hid in a movie theater",
  "How Elvis treated total strangers — the documented acts of generosity nobody talks about",
  "Elvis in the Army — how he refused special treatment and served as a regular soldier",
  "The night Elvis cried on stage and nobody knew why",
  "Elvis and Lisa Marie — the father behind the King",
  "The moment Elvis first heard gospel music and said it changed his life forever",
  "How Elvis treated his band — loyalty stories from Scotty Moore and the original crew",
  "The karate obsession — how Elvis became a legitimate martial artist",
  "Elvis's handwritten letters — what he wrote when nobody was watching",
  "The night Elvis bought Graceland — he was 22 years old",
  "Elvis and James Brown — the mutual respect between the two Kings",
  "How Elvis responded to his harshest critics — the ones who said he would destroy America",
  "The gospel album Elvis insisted on making when no one thought it would sell",
  "Elvis's last Christmas at Graceland — December 1976",
  "The moment Elvis realized his career was in danger — and what he did about it",
  "Elvis and Priscilla — the real story behind the marriage and the divorce"
];

function runDaily() {
  var apiKey = PropertiesService.getScriptProperties().getProperty('OPENROUTER_API_KEY');
  if (!apiKey) throw new Error('OPENROUTER_API_KEY not set in Script Properties.');

  // Pick today's topic (seeded by date so same topic all day)
  var today = new Date();
  var dateStr = Utilities.formatDate(today, 'UTC', 'yyyy-MM-dd');
  var seed = dateStr.split('').reduce(function(acc, c) { return acc + c.charCodeAt(0); }, 0);
  var topic = TOPICS[seed % TOPICS.length];

  Logger.log("Today's topic: " + topic);

  var headers = {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://github.com/elsykes74-cpu/hermes-agent',
    'X-Title': 'The King Lives - Elvis Daily Script'
  };

  // ── 1. Script ────────────────────────────────────────────────────────────────

  var scriptPayload = {
    model: 'anthropic/claude-sonnet-4-6',
    max_tokens: 1000,
    messages: [
      {
        role: 'system',
        content: 'You are the head writer for The King Lives — a faceless Elvis Presley documentary YouTube channel. Write a single 60-second narration script about the assigned topic.\n\nSTRICT RULES:\n- 130 to 150 words exactly\n- No blank lines between sentences — one continuous flowing block of text\n- No stage directions, scene notes, labels, or headers\n- No markdown formatting of any kind\n- Historically accurate — do not invent facts\n- Open with a date, place, or shocking statement — never Elvis\'s name first\n- Cinematic documentary tone — David Attenborough meets true crime\n- End on an emotional gut-punch closing line\n- Output the raw script text and absolutely nothing else'
      },
      { role: 'user', content: "Today's topic: " + topic }
    ]
  };

  var scriptResp = UrlFetchApp.fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'post',
    headers: headers,
    payload: JSON.stringify(scriptPayload),
    muteHttpExceptions: true
  });
  var script = JSON.parse(scriptResp.getContentText()).choices[0].message.content.trim();
  var wordCount = script.split(/\s+/).length;
  Logger.log('Script generated (' + wordCount + ' words)');

  // ── 2. Scene breakdown ───────────────────────────────────────────────────────

  var scenePayload = {
    model: 'anthropic/claude-sonnet-4-6',
    max_tokens: 1000,
    messages: [
      {
        role: 'system',
        content: 'You are a documentary video editor. You receive a 60-second narration script and break it into exactly 7 scenes with timestamps and visual directions.\n\nSTRICT RULES:\n- Exactly 7 scenes\n- Timestamps start at 00:00 and end at 01:00 exactly\n- Visual direction is one concrete sentence describing the image or footage\n- Visual directions must be specific enough to use as image search queries or Higgsfield AI video generation prompts\n- Do not invent content — only use words from the script\n- Output only the scene breakdown in this exact format, nothing else:\n\nScene 1 | 00:00 - 00:05\n[script excerpt]\nVisual direction: [one sentence]\n\nScene 2 | 00:05 - 00:12\n[script excerpt]\nVisual direction: [one sentence]\n\nContinue through Scene 7 ending exactly at 01:00'
      },
      { role: 'user', content: 'Break this script into scenes:\n\n' + script }
    ]
  };

  var sceneResp = UrlFetchApp.fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'post',
    headers: headers,
    payload: JSON.stringify(scenePayload),
    muteHttpExceptions: true
  });
  var sceneBreakdown = JSON.parse(sceneResp.getContentText()).choices[0].message.content.trim();
  Logger.log('Scene breakdown generated');

  // ── 3. Production document ───────────────────────────────────────────────────

  var dateLabel = Utilities.formatDate(today, 'UTC', 'MMMM d, yyyy');
  var divider = '================================================';

  var doc = [
    divider,
    'THE KING LIVES — DAILY PRODUCTION DOCUMENT',
    'Date: ' + dateLabel,
    'Topic: ' + topic,
    divider,
    '',
    'FULL SCRIPT:',
    script,
    '',
    divider,
    '',
    'SCENE BREAKDOWN:',
    sceneBreakdown,
    '',
    divider,
    'PRODUCTION NOTES:',
    'ElevenLabs: speed 0.88 | stability 70% | similarity 65% |',
    'style exaggeration off | speaker boost on',
    'Channel: The King Lives',
    'Format: Faceless documentary | 9:16 vertical',
    divider,
    ''
  ].join('\n');

  // ── 4. Save to Google Drive ──────────────────────────────────────────────────

  var folders = DriveApp.getFoldersByName('Elvis Scripts');
  if (!folders.hasNext()) throw new Error("'Elvis Scripts' folder not found in Google Drive.");
  var folder = folders.next();

  var fileName = dateStr + '_Elvis_Production.txt';
  folder.createFile(fileName, doc, MimeType.PLAIN_TEXT);
  Logger.log('Saved to Drive: Elvis Scripts/' + fileName);
}
