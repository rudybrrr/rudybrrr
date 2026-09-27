"""Everything the README says, written as a model card. Facts come from rudhresh.com's
content (app/_data in portfolio-site); keep them in step. Edit here, then run build.py."""

URL = 'https://www.rudhresh.com'
CASE = URL + '/work/'
GH = 'https://github.com/'
EMAIL = 'rudy.rudhresh@gmail.com'
LINKEDIN = 'https://www.linkedin.com/in/rudhresh-r/'
TELEGRAM = 'https://t.me/rudybrrr'

# The hero: the name as a tokenizer would split it, then one line streamed out.
NAME_TOKENS = [('Rud', 49), ('hresh', 17010), (' R', 431), ('.', 13)]
PROMPT = 'who are you, in one line?'
ANSWER = ('I build full-stack AI products, from the model to the interface, '
          'for teams where being wrong is expensive.')
META = ['Founding Engineer @ BuilderLab', 'Applied AI & Analytics @ SP']

DETAILS = [
    ('Developed by', 'Agne Rudhresh Ravichandran (goes by Rudy), Singapore'),
    ('Model type', 'Full-stack AI engineer: model, system, interface'),
    ('Current checkpoint', f'Founding Engineer at [BuilderLab]({CASE}builderlab), Jul 2026 to now'),
    ('Base model', 'Applied AI & Analytics, Singapore Polytechnic (SP Scholar)'),
    ('Languages', 'Python, TypeScript, English'),
    ('License', 'Open to internships in full-stack AI'),
    ('Card', f'Case studies for everything below live at [rudhresh.com]({URL})'),
]

TRAINING_DATA = [
    'Applied AI & Analytics at Singapore Polytechnic: 4.0 cGPA, six distinctions',
    'SP AI Club: Head of Operations, 6+ workshops of 30 to 60 students',
    'SP Outstanding Talent (SPOT): Leadership Development Coordinator, ExCo',
    'Singapore Youth AI: INSPIRE Coordinator, sessions of 110+ students',
    'Five hackathons in 2026, and counting',
]

# Checkpoints on the (illustrative) loss curve: (year, month, label, label row).
# Rows 0 and 1 sit in a lane under the curve; -1 goes above it.
CHECKPOINTS = [
    (2025, 6, 'joins the SP AI Club committee', 0),
    (2025, 10, 'F1 Singapore GP: keeps the gates scanning', 0),
    (2026, 2, 'starts Stride; Head of Ops, SPAI', 0),
    (2026, 6, '5-day game jam: spike, then 1st', -1),
    (2026, 7, 'Founding Engineer, BuilderLab', 1),
]

EVALUATION = [
    ('cGPA, Applied AI & Analytics', '**4.0**', 'SP Scholar, six distinctions'),
    ('Director’s Honour Roll', '**Top 10%**', 'School of Computing, AY2025/26'),
    ('BuildingBloCS Game Jam 2026', '**1st**, CSIT category', f'with [Breach]({CASE}breach), a team of four'),
    ('ReRoute allocator vs median greedy', '**+4.12%**', 'expected preserved connections; synthetic benchmark, 2,500 worlds'),
    ('ReRoute test suite', '**645** passing', '541 backend, 104 frontend; they test the authority boundaries'),
]

DEPLOYMENTS = [
    ('BuilderLab', CASE + 'builderlab', 'Founding Engineer, Jul 2026 to now',
     'Backend, architecture and security in a live codebase, where the paths that move money have to be right.'),
    ('BookMyShow Southeast Asia', CASE + 'bookmyshow', 'Access control, F1 Singapore GP 2025',
     'Kept entry running at the Formula 1 Singapore Grand Prix, one networked scanner at a time.'),
]


def t(name, slug, setting, claim, repo=None, case=True):
    return {'name': name, 'href': CASE + slug if case else repo, 'setting': setting, 'claim': claim,
            'repo': repo if case else None}


TASKS = [
    ('Hackathons', 'Built against the clock, judged on stage.', True, [
        t('ReRoute', 'reroute', 'PSA Code Sprint 2.0, 2026',
          'Recovers a transshipment plan after a late vessel, without letting the model pick the container.',
          GH + 'rudybrrr/psa-cs-ministryofmeat'),
        t('Breach', 'breach', 'BuildingBloCS 2026, 1st in CSIT',
          'A multiplayer cyber-defence lab where the server, not the players, decides what happened.',
          GH + 'Inferno1172/Pygame_P17'),
        t('Remember', 'remember', 'Daytona HackSprint, 2026',
          'Brings a dormant GitHub app back to life in a sandbox, or refuses honestly when it can’t be made safe.',
          GH + 'pufferfish3e/daytona-hacakthon'),
        t('Orin', 'orin', 'Push to Prod, 2026',
          'One meeting in, four briefings out, each built for what that role has to act on.',
          GH + 'pufferfish3e/pushtoprodjava'),
        t('ORGIS', 'orgis', 'strAIght up!, 2026',
          'Every chat app in one queue, sorted by what needs a reply first.',
          GH + 'rudybrrr/straight-up-hackathon-ybg'),
    ]),
    ('Products', 'Shipped end to end, auth to interface.', True, [
        t('Stride', 'stride', 'Independent, 2026',
          'One workspace where a task, the time planned for it and the session spent on it are the same record.',
          GH + 'rudybrrr/stride'),
        t('Cosmic Quest', 'cosmic-quest', 'Backend engineering, 2026',
          'A wellness game whose backend remembers every step you took to reach the next planet.',
          GH + 'rudybrrr/cosmic-quest'),
    ]),
    ('Machine learning', 'Controlled experiments before claims.', False, [
        t('GAN vs VAE', 'gan-vs-vae', 'CIFAR-10, two-person, 2026',
          'Two generative models judged by one protocol that was locked before either could win.',
          GH + 'rudybrrr/cifar10-gan-vs-vae'),
        t('Kuzushiji OCR', 'kuzushiji-ocr-cnn-vs-crnn', 'CNN vs CRNN, 2026',
          'Does a recurrent layer help read cursive Japanese, and does the help grow with length?',
          GH + 'rudybrrr/kuzushiji-ocr-cnn-vs-crnn'),
        t('Pendulum DQN', 'pendulum-dqn-gravity-control', 'Reinforcement learning, 2026',
          'Can one frozen DQN recipe balance a pendulum when gravity changes?',
          GH + 'rudybrrr/pendulum-dqn-gravity-control'),
        t('Pizza Review Sentiment', 'multilingual-pizza-review-sentiment-rnn', 'English and Malay, 2026',
          'Three-way sentiment where the hard part is the middle.',
          GH + 'rudybrrr/multilingual-pizza-review-sentiment-rnn'),
        t('Handwritten Letter CNN', 'handwritten-letter-classification-cnn', 'EMNIST letters, 2026',
          'Twenty-six letters, from a dense baseline to a locked CNN.',
          GH + 'rudybrrr/handwritten-letter-classification-cnn'),
        t('Applied Machine Learning', 'applied-machine-learning', 'Four problem types, 2025',
          'Baseline first, compare before choosing, then explain the choice.',
          GH + 'rudybrrr/applied-machine-learning'),
    ]),
    ('Data and analytics', 'Numbers read together, not ranked alone.', False, [
        t('Client Portfolio Prioritisation', 'client-portfolio-prioritisation', 'Plotly and Dash, 2026',
          'Which clients to protect, grow, fix or question: nine charts that answer it as one story.',
          GH + 'rudybrrr/it-systems-integrator-plotly-dashboard'),
        t('Career & Labour-Market Analysis', 'career-and-labour-market-analysis', 'Data analysis, 2025',
          'Pay, flexibility, demand and job security, read together rather than ranked on salary.',
          GH + 'rudybrrr/career-and-labour-market-analysis'),
    ]),
    ('Still training', 'Newer repos, not written up yet.', False, [
        t('restock-ai', '', 'Python, 2026', 'Adaptive restaurant inventory and procurement agent.',
          GH + 'rudybrrr/restock-ai', case=False),
        t('staged', '', 'TypeScript, 2026',
          'Local-first, cost-aware workbench for auditing AI-generated code changes before commit.',
          GH + 'rudybrrr/staged', case=False),
        t('spec-ingest-verify', '', 'Python, 2026', 'Specification ingestion and verification.',
          GH + 'rudybrrr/spec-ingest-verify', case=False),
    ]),
]

# The toolbox as a hand-placed 2D "embedding": cluster -> (centre x, y in 0..1, tools).
EMBEDDING = {
    'modelling': (0.2, 0.3, ['Python', 'TensorFlow', 'Keras', 'Plotly', 'Dash', 'OR-Tools']),
    'systems': (0.72, 0.26, ['FastAPI', 'Pydantic', 'SQLModel', 'asyncio', 'WebSockets', 'Express', 'MySQL']),
    'product': (0.7, 0.76, ['Next.js', 'React', 'TypeScript', 'Supabase', 'Clerk', 'Vitest']),
    'LLMs': (0.22, 0.76, ['OpenAI', 'Claude', 'Groq Whisper', 'Daytona']),
}

INTENDED = [
    'Internships in full-stack AI, from the model to the interface.',
    'Backend and systems work where the failure paths matter: money, access, safety.',
    'Hackathon teams whose demo has to actually run on stage.',
]
OUT_OF_SCOPE = [
    'Letting a language model make the final call on anything expensive. The model proposes; the system decides.',
    'Claims without a baseline.',
]
LIMITATIONS = [
    '“A man who has not hit his Claude limit by noon has wasted his morning.” (Aristotle, probably.) Usually hit before noon.',
    'Latency rises on ride nights. Longest run so far: 101 km in 4:59:56.',
    'Will ask what the baseline is. Then what the p90 is.',
    'Trained mostly on Singapore data; generalises with context.',
]
