"""Everything the README says. Facts come from rudhresh.com's content (app/_data in
portfolio-site); keep them in step with it. Edit here, then run build.py."""

SITE = {
    'name': 'Rudhresh R.',
    'full_name': 'Agne Rudhresh Ravichandran',
    'role': 'Full-Stack AI Engineer',
    'role_lines': ['Full-Stack', 'AI Engineer'],
    'status': 'Open to internships',
    'focus': 'Full-Stack AI',
    'status_lines': ['Founding Engineer at BuilderLab', 'Applied AI & Analytics, Singapore Polytechnic'],
    'email': 'rudy.rudhresh@gmail.com',
    'url': 'https://www.rudhresh.com',
    'linkedin': 'https://www.linkedin.com/in/rudhresh-r/',
    'telegram': 'https://t.me/rudybrrr',
    'links': ['rudy.rudhresh@gmail.com', 'LinkedIn ↗', 'Telegram ↗', 'rudhresh.com ↗'],
    'motto': '“A man who has not hit his Claude limit by noon has wasted his morning.” Aristotle, probably',
}

STATEMENT = ('I build full-stack AI products, from the model to the interface, that feel inevitable '
             'and stay reliable for teams where being wrong is expensive.')

# (text, is_fact): facts sit in full ink, the glue between them is quiet.
PROOF = [
    ('Founding Engineer at BuilderLab,', True), ('on', False), ('backend, architecture and security.', True),
    ('Studying', False), ('Applied AI & Analytics', True), ('as an', False), ('SP Scholar,', True),
    ('with a', False), ('4.0 cGPA', True), ('and', False), ('1st at the BuildingBloCS Game Jam.', True),
]

BUILD = {
    'heading': ['Models become systems.', 'Systems disappear in use.'],
    'steps': [
        {'word': 'Model', 'tools': ['Python', 'TensorFlow', 'Keras'],
         'body': 'Controlled experiments before claims: one shared protocol, frozen recipes, and metrics that say where a model actually stands.'},
        {'word': 'System', 'tools': ['FastAPI', 'OR-Tools', 'OpenAI'],
         'body': 'The model proposes, the system decides. Typed APIs, solvers and checks keep the output feasible.'},
        {'word': 'Product', 'tools': ['Next.js', 'Supabase', 'Clerk'],
         'body': 'Auth, data and interface shipped end to end, until the system disappears in use.'},
    ],
}

FLAGSHIPS = [
    {'name': 'ReRoute', 'line': 'Delay recovery where the solver decides, not the model.', 'label': 'AI Systems'},
    {'name': 'GAN vs VAE', 'line': 'Two generative models, one controlled protocol.', 'label': 'Machine Learning'},
    {'name': 'Stride', 'line': 'Tasks, calendar and focus in one workspace.', 'label': 'Product'},
    {'name': 'Breach', 'line': 'A multiplayer cyber-defence lab where the server decides what happened.', 'label': '1st, BuildingBloCS'},
]

SITE_WORK = 'https://www.rudhresh.com/work/'
GH = 'https://github.com/'


def p(id, name, context, year, claim, repo=None, case=True):
    return {'id': id, 'name': name, 'context': context, 'year': year, 'claim': claim,
            'href': SITE_WORK + id if case else repo, 'repo': repo}


CATEGORIES = [
    {'id': 'work', 'name': 'Work', 'line': 'Where the paths that matter have to be right.', 'items': [
        p('builderlab', 'BuilderLab', 'Founding Engineer', '2026–',
          'Backend, architecture and security in a live early-stage codebase, where the paths that move money have to be right.'),
        p('bookmyshow', 'BookMyShow Southeast Asia', 'F1 Singapore Grand Prix', '2025',
          'Keeping entry running at the Formula 1 Singapore Grand Prix, one networked scanner at a time.'),
    ]},
    {'id': 'hackathons', 'name': 'Hackathons', 'line': 'Built against the clock, judged on stage.', 'items': [
        p('reroute', 'ReRoute', 'PSA Code Sprint 2.0', '2026',
          'When a late vessel breaks a transshipment plan, recover it without letting the model pick the container.',
          GH + 'rudybrrr/psa-cs-ministryofmeat'),
        p('breach', 'Breach', 'BuildingBloCS, 1st in CSIT', '2026',
          'A multiplayer cyber-defence lab where the server, not the players, decides what happened.',
          GH + 'Inferno1172/Pygame_P17'),
        p('remember', 'Remember', 'Daytona HackSprint', '2026',
          'Paste a dormant GitHub app; get it back running in a sandbox, or an honest refusal when it can’t be made safe.',
          GH + 'pufferfish3e/daytona-hacakthon'),
        p('orin', 'Orin', 'Push to Prod Hackathon', '2026',
          'One meeting in; four briefings out, each built for what that role has to act on.',
          GH + 'pufferfish3e/pushtoprodjava'),
        p('orgis', 'ORGIS', 'strAIght up! Hackathon', '2026',
          'Every chat app in one queue, sorted by what needs a reply first.',
          GH + 'rudybrrr/straight-up-hackathon-ybg'),
    ]},
    {'id': 'products', 'name': 'Products', 'line': 'Shipped end to end, auth to interface.', 'items': [
        p('stride', 'Stride', 'Independent', '2026',
          'One workspace where a task, the time you plan for it and the session you spend on it are the same record.',
          GH + 'rudybrrr/stride'),
        p('cosmic-quest', 'Cosmic Quest', 'Backend engineering', '2026',
          'A wellness game whose backend has to remember every step you took to reach the next planet.',
          GH + 'rudybrrr/cosmic-quest'),
    ]},
    {'id': 'ml', 'name': 'Machine learning', 'line': 'Controlled experiments before claims.', 'items': [
        p('gan-vs-vae', 'GAN vs VAE', 'Two-person, CIFAR-10', '2026',
          'Two generative models on CIFAR-10, judged by one protocol that was locked before either could win.',
          GH + 'rudybrrr/cifar10-gan-vs-vae'),
        p('kuzushiji-ocr-cnn-vs-crnn', 'Kuzushiji OCR', 'CNN vs CRNN', '2026',
          'Does a recurrent layer help read cursive Japanese sequences, and does the help grow with length?',
          GH + 'rudybrrr/kuzushiji-ocr-cnn-vs-crnn'),
        p('pendulum-dqn-gravity-control', 'Pendulum DQN', 'Reinforcement learning', '2026',
          'Can one frozen DQN recipe balance a pendulum when gravity changes?',
          GH + 'rudybrrr/pendulum-dqn-gravity-control'),
        p('multilingual-pizza-review-sentiment-rnn', 'Pizza Review Sentiment', 'English and Malay RNN', '2026',
          'Three-way sentiment for English and Malay pizza reviews, where the hard part is the middle.',
          GH + 'rudybrrr/multilingual-pizza-review-sentiment-rnn'),
        p('handwritten-letter-classification-cnn', 'Handwritten Letter CNN', 'EMNIST letters', '2026',
          'Twenty-six handwritten letters, from a dense baseline to a locked CNN.',
          GH + 'rudybrrr/handwritten-letter-classification-cnn'),
        p('applied-machine-learning', 'Applied Machine Learning', 'Four problem types', '2025',
          'Four problem types, one discipline: baseline first, compare before choosing, then explain the choice.',
          GH + 'rudybrrr/applied-machine-learning'),
    ]},
    {'id': 'data', 'name': 'Data & analytics', 'line': 'Numbers read together, not ranked alone.', 'items': [
        p('client-portfolio-prioritisation', 'Client Portfolio Prioritisation', 'Plotly and Dash', '2026',
          'Which clients should management protect, grow, fix or question? Nine charts that answer it as one story.',
          GH + 'rudybrrr/it-systems-integrator-plotly-dashboard'),
        p('career-and-labour-market-analysis', 'Career & Labour-Market Analysis', 'Data analysis', '2025',
          'Pay, flexibility, demand and job security, read together rather than ranked on salary alone.',
          GH + 'rudybrrr/career-and-labour-market-analysis'),
    ]},
    {'id': 'workshop', 'name': 'On the bench', 'line': 'Newer repos, not written up yet.', 'items': [
        p('restock-ai', 'Restock AI', 'Python agent', '2026',
          'Adaptive restaurant inventory and procurement agent.', GH + 'rudybrrr/restock-ai', case=False),
        p('staged', 'Staged', 'TypeScript', '2026',
          'A cost-aware AI verification workbench for auditing AI-generated code changes before commit.',
          GH + 'rudybrrr/staged', case=False),
        p('spec-ingest-verify', 'Spec Ingest Verify', 'Python', '2026',
          'Specification ingestion and verification.', GH + 'rudybrrr/spec-ingest-verify', case=False),
    ]},
]

STACK = [
    ['Python', 'TensorFlow', 'Keras', 'FastAPI', 'Pydantic', 'OR-Tools CP-SAT', 'OpenAI', 'Claude', 'Plotly'],
    ['Next.js', 'React', 'TypeScript', 'Supabase', 'Clerk', 'Vitest', 'Express', 'MySQL', 'WebSockets'],
]

ALONG = [
    {'name': 'Recognition', 'rows': [
        ('SP Scholarship', 'Singapore Polytechnic, merit-based'),
        ('BuildingBloCS Game Jam 2026', '1st Place, CSIT Category'),
        ('Director’s Honour Roll', 'Top 10% of cohort, AY2025/26'),
        ('Academic Distinctions', 'Top 5%, AY2025/26'),
    ]},
    {'name': 'Leadership', 'rows': [
        ('Singapore Polytechnic AI Club', 'Head of Operations'),
        ('SP Outstanding Talent (SPOT)', 'Leadership Development Coordinator, ExCo'),
        ('Singapore Youth AI', 'INSPIRE Coordinator, 110+ students a session'),
    ]},
    {'name': 'Off the keyboard', 'rows': [
        ('Long night rides', 'Best so far: 101 km in 4:59:56'),
    ]},
]
