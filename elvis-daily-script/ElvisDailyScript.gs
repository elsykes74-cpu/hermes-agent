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
  "Elvis and Priscilla — the real story behind the marriage and the divorce",
  "What Colonel Tom Parker never told Elvis — the secret that controlled his entire career",
  "The Ed Sullivan Show, September 9, 1956 — the night 60 million Americans stopped breathing",
  "The day Elvis met The Beatles — August 27, 1965, Perugia Way, Beverly Hills",
  "The 1968 Comeback Special — how Elvis walked back into the world in a black leather suit",
  "Jesse Garon Presley — the twin brother Elvis never forgot and always carried",
  "The Las Vegas residency, 1969 — how Elvis sold out 57 shows and reinvented himself at 34",
  "The Memphis Mafia — the men who lived with Elvis, protected him, and watched him disappear",
  "The recording of Suspicious Minds — the last number one of his life, October 1969",
  "Elvis and Tom Jones — the friendship between two voices that shook the world",
  "The Million Dollar Quartet — December 4, 1956, when Elvis, Cash, Perkins, and Lewis shared one mic",
  "Aloha from Hawaii — January 14, 1973, the first concert broadcast live via satellite to the world",
  "Elvis's final concert — June 26, 1977, Market Square Arena, Indianapolis",
  "The night Elvis rented out the entire Memphis fairground so his friends could ride all night",
  "How Elvis learned to move — the untold story of where those hips came from",
  "Elvis and Sammy Davis Jr. — the friendship that crossed every color line in 1950s America",
  "The making of Jailhouse Rock — and how Elvis almost didn't survive the filming",
  "Elvis's reading list — the spiritual books, the philosophy, the search for something he never named",
  "The night Elvis gave away a $10,000 car to a stranger in a Memphis parking lot",
  "How Elvis handled fame — the bodyguards, the gates, the loneliness inside Graceland",
  "Elvis and Frank Sinatra — from sworn enemies to mutual respect in five years",
  "The haircut heard round the world — Elvis enters the Army, March 24, 1958",
  "Scotty Moore, Bill Black, and DJ Fontana — the three men who built the sound of rock and roll",
  "The night Elvis performed for 50,000 people in Hawaii before he even released a record there",
  "Elvis's first television appearance — The Dorsey Brothers Stage Show, January 28, 1956",
  "The Loving You recording sessions — how Elvis put his whole childhood into one film",
  "How Priscilla survived Graceland — what she has said about those years behind closed doors",
  "The day Elvis called his old school and donated a fully equipped music room anonymously",
  "Elvis and Muhammad Ali — two men who changed America standing in the same room",
  "The dark years, 1971-1974 — what was really happening behind the sequined jumpsuits",
  "How Elvis's voice changed — the raw teenager, the matured baritone, and the final cry",
  "The night Elvis stopped a fight in a gas station and nobody believed the witness",
  "Roy Orbison opening for Elvis — what Roy said about watching him perform from the wings",
  "Elvis in Germany — Priscilla, the loneliness, and the pills that started everything",
  "The unreleased recordings — what Elvis recorded that the world has never heard",
  "How Elvis built Graceland into a home — room by room, decision by decision",
  "The last photo session — August 1977, the images that shocked the world",
  "Elvis and his father Vernon — the complicated love between a son who made millions and a father who never understood it",
  "How Elvis treated every hotel staff member wherever he stayed — the tips, the conversations, the respect",
  "The gospel roots — how Mahalia Jackson and the Blackwood Brothers shaped everything Elvis became",
  "Elvis's favorite meal — fried peanut butter banana sandwiches and the cook who made them for 20 years",
  "The night Elvis called his fans back to the stage and sang for three hours just because he didn't want to stop",
  "How Elvis prepared for a show — the rituals, the prayers, the moment before the curtain",
  "B.B. King and Elvis — two boys from Mississippi who changed music and never forgot where they came from",
  "The Sun Sessions outtakes — the songs that were too raw, too wild, too dangerous to release in 1954",
  "Elvis and the press — how he handled reporters who came to destroy him and left as believers",
  "The night Elvis paid off a stranger's mortgage and asked the bank manager never to tell anyone",
  "How Elvis's movies made him miserable — the 31 films he made and the music he gave up to make them",
  "Charlie Hodge — the man who handed Elvis water and scarves for 17 years and never left his side",
  "Elvis's relationship with God — the prayers, the doubts, the gospel, the seeking",
  "The Comeback Special rehearsals — the days when Elvis rediscovered who he was",
  "How Jerry Schilling became part of the Memphis Mafia and what he saw in 20 years beside Elvis",
  "The night Elvis sang Amazing Grace and the entire audience forgot they were at a rock concert",
  "Elvis and Ann-Margret — the on-set romance that almost changed both their lives forever",
  "The recording of In The Ghetto — Elvis's most political moment and what it cost him",
  "How Graceland's gates got the musical notes — the detail Elvis personally approved",
  "The last time Elvis saw his mother alive — and what he said at her funeral",
  "How Larry Geller introduced Elvis to spiritual philosophy and changed the last decade of his life",
  "The '68 Special sit-down session — Elvis, no script, just guitar and the audience, the most raw he ever was on camera",
  "Elvis and the racial divide — how a white boy from Mississippi used Black music to break American segregation open",
  "The Tupelo homecoming concert, September 26, 1956 — returning to the town that couldn't have imagined this",
  "How Elvis's generosity nearly bankrupted him — the cars, the houses, the cash, the endless giving",
  "Ginger Alden — the last person to see Elvis alive and what she has said about that morning",
  "The night Elvis walked into a Memphis diner at 3am and cooked breakfast for the whole staff",
  "How Elvis responded when a concertgoer threw something at him on stage — what he did next silenced the room",
  "The secret studio sessions — when Elvis recorded alone, late at night, with no audience and no pressure",
  "Elvis and country music — how Nashville originally rejected him and eventually claimed him as its greatest son",
  "The jumpsuits — who designed them, what they meant, and the night one split on stage mid-show",
  "How Elvis's childhood in Tupelo shaped everything — the shotgun house, the poverty, the church, the music",
  "The American Sound Studio sessions, 1969 — the week Elvis made his greatest recordings and everyone knew it",
  "Elvis's relationship with his fans — the letters he read, the people he met at the gate, the names he remembered",
  "The night Elvis was offered a role in a serious film and chose not to take it — and why",
  "How Red West, Sonny West, and Dave Hebler were fired and what happened when their book came out",
  "Elvis and the TCB lightning bolt — what 'Taking Care of Business' really meant to him and his crew",
  "The final recordings — what Elvis sang in the studio in the last months of his life",
  "August 16, 1977 — what happened at Graceland that day, hour by hour, as the world lost the King"
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

function myFunction() {
  runDaily();
}
