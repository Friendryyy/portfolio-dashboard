"""
build_source_pages.py
สร้าง Database/sources/{TICKER}.md — dedicated research source page ต่อหุ้น
แต่ละ link มี: title, สรุปสั้นๆ เกี่ยวข้องกับ thesis ยังไง, tags
"""
import re, os

def extract_link_descriptions(filepaths):
    link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
    url_to_desc = {}
    for fp in filepaths:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            for match in link_pattern.finditer(content):
                text, url = match.group(1), match.group(2)
                url = url.strip()
                if url not in url_to_desc and len(text.strip()) > 3 and not text.startswith('http'):
                    url_to_desc[url] = text.strip()
        except:
            pass
    return url_to_desc

def get_tags(url, desc):
    tags = []
    c = (url + ' ' + (desc or '')).lower()
    if 'youtube.com' in c: tags.append('#youtube')
    if 'sec.gov' in c: tags.append('#sec')
    if any(x in c for x in ['investor.', 'abc.xyz', 'newsroom', 'news-release', 'quarterly-results', 'financial-results', '/ir/']): tags.append('#IR')
    if any(x in c for x in ['earnings', 'q1 ', 'q2 ', 'q3 ', 'q4 ', 'revenue', 'guidance', 'transcript', 'results', 'fy20']): tags.append('#earnings')
    if any(x in c for x in ['valuation', 'p/e', 'dcf', 'pe ratio', 'fair value', 'price target', 'forward pe', 'statistics', 'macrotrends', 'gurufocus', 'alphaspread']): tags.append('#valuation')
    if any(x in c for x in ['analyst', 'rating', 'upgrade', 'downgrade', 'raised to buy', 'bull', 'forecast', 'target']): tags.append('#analyst')
    if any(x in c for x in ['risk', 'short', 'muddy waters', 'probe', 'doj', 'antitrust', 'regulation', 'fda', 'export control', 'china', 'zero market share', 'charge', 'investigation', 'concern']): tags.append('#risk')
    if any(x in c for x in ['moat', 'competitive', 'market share', 'advantage', 'competitor', ' vs ', 'peer', 'cuda']): tags.append('#moat')
    if any(x in c for x in ['macro', 'fed', 'rate', 'inflation', 'gdp', 'geopolit', 'war', 'tariff', 'policy', 'iran', 'taiwan', 'israel', 'trump', 'xi']): tags.append('#macro')
    if any(x in c for x in ['insider', '13f', 'institutional', 'holder', 'ownership', 'fintel', 'short interest']): tags.append('#smartmoney')
    if any(x in c for x in ['sector', 'industry', 'market size', 'tam', 'space', 'satellite', 'defense', 'glp-1', 'obesity', 'ai chip', 'fintech', 'cloud', 'semiconductor', 'golden dome', 'launch']): tags.append('#sector')
    if any(x in c for x in ['technical', 'rsi', 'macd', 'support', 'resistance', 'chart', 'cheat-sheet', 'barchart']): tags.append('#technicals')
    if any(x in c for x in ['acqui', 'merger', 'deal', 'contract', 'award', 'partnership', 'motiv', 'anduril']): tags.append('#catalyst')
    if any(x in c for x in ['waymo', 'gemini', 'deepmind', 'i/o', 'blackwell', 'neutron', 'bluebird', 'wegovy', 'ozempic', 'semaglutide', 'aip', 'gotham', 'foundry', 'prime video', 'aws']): tags.append('#product')
    if any(x in c for x in ['fool.com', 'benzinga', 'marketbeat', '247wallst', 'investing.com', 'bloomberg', 'cnbc', 'reuters', 'wsj', 'fortune', 'seekingalpha', 'stocktwits', 'coindesk', 'satnews', 'airforce', 'spacefl']): tags.append('#news')
    if not tags: tags.append('#news')
    return ' '.join(sorted(set(tags)))

# Summaries: known descriptions per ticker + URL keyword → what it covers for the thesis
KNOWN_SUMMARIES = {
    # NVDA
    'tomshardware.com': 'Jensen CEO ยืนยัน NVDA มี market share 0% ในจีน + export policy "backfired" → ใช้เป็น evidence สำหรับ China Risk',
    'futurumgroup.com/insights/nvidia-q3': 'Q3 FY2026 earnings — Data Center revenue record, Q4 guidance; ฐานข้อมูล earnings momentum',
    'foreignpolicyjournal.com/2026/04/26/nvidia': 'Analyst upgrade NVDA เป็น BUY — export controls เปลี่ยนเส้นทาง Blackwell supply มา US/Europe แทนจีน',
    'investor.nvidia.com': 'Official NVDA IR — Financial Reports หน้าหลัก SEC filings',
    'nvidianews.nvidia.com/news/nvidia-announces': 'FY2026 Full Year Results official — Revenue $193.7B +68%, Data Center 88% of total',
    'nvidianews.nvidia.com': 'NVDA Q1 FY2026 Results official — source for earnings baseline',
    'sec.gov/Archives/edgar': 'SEC CFO Commentary Q1 FY2026 — official guidance + margin breakdown',
    'analyticsinsight.net': 'Technical analysis — NVDA $198-201, breakout vs resistance level',
    'gurufocus.com': 'Forward P/E historical comparison — ใช้ compare ว่า valuation ถูกกว่า avg 5Y ยังไง',
    'fxleaders.com': 'NVDA ติด $200 resistance — China lockout + trade risks กดราคา short-term',
    # RKLB
    'stocktitan.net/news/RKLB/rocket-lab-announces': 'Q1 2026 Earnings official — Revenue record, Neutron on-track confirmation',
    'stocktitan.net/news/RKLB/rocket-lab-to-acquire': 'RKLB acquire Motiv Space Systems (robotics) — ขยาย Space Systems segment',
    'investing.com/news/company-news/rocket-lab-q1-2026': 'Q1 2026 slides — Revenue +64%, Backlog $2.2B; ใช้เป็น earnings evidence',
    'rocketlabcorp.com/updates/rocket-lab-awarded-816m': 'RKLB ได้ $816M prime contract กับ US Space Force — Golden Dome program; catalyst หลัก',
    'fool.com/investing/2026/05/02/why-rocket-lab-stock-zoomed-285': 'วิเคราะห์ว่าทำไม RKLB ขึ้น 285% ใน April — earnings + contract catalyst',
    'fool.com/investing/how-to-invest/stocks/rocket-lab': 'Motley Fool RKLB long-term forecast + thesis summary',
    'bloomberg.com': 'Bloomberg — RKLB earnings beat, Neutron on track for 2026; institutional source',
    'seekingalpha.com': 'Seeking Alpha pre-earnings setup analysis — bullish thesis',
    'csps.aerospace.org': 'Aerospace Corp — FY2026 Defense Space Budget analysis, Golden Dome context',
    'orbital-intel.com': 'SpaceX vs Rocket Lab — competitive analysis, moat comparison',
    'tipranks.com': 'Morgan Stanley turns bullish on space stocks (RKLB, ASTS, LUNR) — institutional upgrade',
    'airandspaceforces.com/space-force-reveals': 'Space Force Golden Dome award details — RKLB prime contractor confirmed',
    'airandspaceforces.com/space-force-spending': 'Space Force budget hitting $40B in 2026 — tailwind for RKLB',
    'marketbeat.com/stock-ideas/5-space-stocks': '5 space stocks ahead of SpaceX IPO — RKLB positioning',
    '247wallst.com/investing/2026/05/08/rocket-lab': 'RKLB +30% day — comparison vs LUNR, Planet Labs performance',
    # ASTS
    'cnbc.com/2026/04/20/ast-falls': 'Blue Origin puts BlueBird 7 in wrong orbit — ASTS -X% — launch failure risk',
    'spaceflightnow.com': 'Spaceflight Now — Blue Origin New Glenn details of BlueBird wrong-orbit incident',
    'satnews.com/2026/05/07': 'ASTS pivots from Blue Origin → SpaceX สำหรับ mid-June launch of 3 BlueBird satellites',
    'fool.com/investing/2026/05/06/have-ast-spacemobiles': 'Motley Fool — ASTS 2026 launch plan assessment post-failure',
    'foreignpolicyjournal.com/2026/05/08': 'ASTS $74 ราคา surges แต่ satellite setbacks + SpaceX IPO risk — balanced view',
    'coherentmarketinsights.com': 'Satellite Internet Market TAM — used for ASTS TAM estimate',
    'tradingkey.com': 'Starlink/SpaceX IPO context — competitive risk for ASTS',
    'techi.com/spacex-ipo': 'SpaceX IPO analysis — competitive threat timeline for ASTS',
    'satnews.com/2026/04/09': 'FCC modernizes satellite spectrum rules — regulatory tailwind for ASTS/RKLB',
    'foreignpolicyjournal.com/2026/05/02': 'FCC spectrum overhaul → ASTS/RKLB/LUNR stock surges; regulatory catalyst',
    'fool.com/earnings/call-transcripts/2026/05/11/ast-spacemobile': 'ASTS Q1 2026 Earnings Call Transcript — official guidance, 45 BlueBirds target',
    'satellitetoday.com': 'ASTS confirms 45 BlueBirds target for 2026 despite Blue Origin failure',
    'wallstreetzen.com': 'ASTS stock forecast + analyst consensus',
    'fintel.io/ss/us/asts': 'ASTS short interest data — 13% short float; smart money positioning',
    # SOFI
    'muddywatersresearch.com': 'Muddy Waters short report (March 2026) — 11 unanswered questions on SOFI accounting; THESIS BREAKER source',
    'investors.sofi.com/news/news-details/2026': 'SoFi official response to Muddy Waters — company rebuttal',
    'fortune.com/2026/03/25/muddy-waters-sofi': 'Fortune — Muddy Waters SOFI accounting concern summary',
    'coindesk.com': 'SoFi crypto business relaunch — $121.6M Q1 revenue; new revenue stream',
    'ainvest.com': 'SOFI credit quality + long-term profitability path analysis',
    '247wallst.com/investing/2026/04/29/sofi': 'SOFI -9% after Q1 earnings — sell-on-beat pattern; technical behavior note',
    'cnbc.com/2026/04/29/sofi-ceo': 'SoFi CEO defends holding guidance steady despite stock drop',
    '247wallst.com/investing/2026/05/12/truist': 'Truist cuts SOFI PT to $17 — loan platform slowdown pressures bull case',
    'investors.sofi.com/news/news-details/2025': 'SoFi launches stablecoin infrastructure — fintech expansion pivot',
    # NVO
    'cnbc.com/2026/05/06/wegovy-glp1': 'CNBC — Wegovy/GLP-1 market outlook, NVO earnings + Ozempic competition update',
    'cnbc.com/2026/02/23/novo-nordisk-stock-cagrisema': 'CagriSema trial disappoints — NVO stock falls; key thesis risk event',
    'biotechreality.com': 'NVO clinical trials ECO 2026 update — pipeline progress review',
    'fiercepharma.com': 'Medicare price reductions on semaglutide — IRA drug pricing risk for NVO',
    'cnbc.com/2025/11/26/why-medicare-price': 'Medicare IRA pricing impact on NVO revenue — regulatory risk analysis',
    # UNH
    'cnbc.com/2026/04/21/unitedhealth-group': 'UNH Q1 2026 earnings — miss + DOJ probe update; ใช้ประกอบ thesis breaker',
    'marketbeat.com/stocks/NYSE/UNH/forecast': 'UNH analyst consensus PT — mean $387 (ราคา $401 เกิน PT แล้ว); valuation signal',
    'unitedhealthgroup.com/newsroom': 'Official UNH Q1 2026 earnings release — revenue, MLR, guidance',
    'healthcaredive.com': 'UNH Medicare Advantage troubles Q4 2025 — MLR expansion context',
    # GOOGL
    'abc.xyz/investor': 'Alphabet Official IR — Annual Reports, SEC filings, Earnings',
    'io.google/2026': 'Google I/O 2026 Official — Product launches: Gemini 2.5, Android XR, AI Overviews; catalyst event May 20-21',
    'waymo.com/blog': 'Waymo raises $1.6B (Feb 2026) — Alphabet optionality asset valuation',
    # AMZN
    'cnbc.com/2026/04/29/amazon': 'Amazon Q1 2026 earnings — AWS growth, operating income; key fundamental source',
    'ir.aboutamazon.com': 'Amazon Official Q1 2026 earnings release — revenue $187.8B, AWS +17%',
    'alphaspread.com': 'AMZN DCF intrinsic value — base case valuation model',
    '247wallst.com/investing/2026/05/05/amazons-free-cash-flow': 'Amazon FCF collapse $26B → $1.2B — CapEx surge concern; key risk data',
    # PLTR
    'cnbc.com/2026/05/04/palantir': 'PLTR Q1 2026 earnings — 85% revenue growth; official results',
    'bloomberg.com/news/articles/2026-05-04/palantir': 'Bloomberg — PLTR strong revenue outlook 2026; institutional view',
    'investing.com/news/company-news/palantir-q1-2026': 'PLTR Q1 slides — 85% growth, stock drops 57% (P/S too high); valuation vs growth',
    'cnbc.com/2026/05/05/why-palantirs-stock': 'CNBC — Why PLTR dropped despite stellar Q1; P/S >100x thesis',
    'fool.com/investing/2026/05/08/palantir-just-crushed': 'Motley Fool — PLTR earnings beat but expensive; hold thesis',
    'io-fund.com': 'IO Fund — PLTR 2026 forecast + AIP platform adoption analysis',
    'kalkine.com': 'Kalkine — PLTR AIP momentum + valuation reality check; balanced thesis',
}

url_pattern = re.compile(r'https?://[^\s\)\]\>\"\' ]+')

configs = {
    'NVDA': {
        'output_files': ['output/2026-05-06_NVDA_analysis.md'],
        'sources_txt': ['tools/NVDA_sources.txt'],
        'session': '2026-05-06',
        'company': 'NVIDIA Corporation',
        'thesis_one_liner': 'AI chip monopoly (CUDA moat), Blackwell supercycle — risk: China export ban, valuation',
    },
    'RKLB': {
        'output_files': ['output/2026-05-08_RKLB_monitoring_update.md', 'output/2026-05-09_space_industry_analysis.md'],
        'sources_txt': ['tools/RKLB_sources.txt'],
        'session': '2026-05-09',
        'company': 'Rocket Lab USA',
        'thesis_one_liner': 'End-to-end space company (launch + systems), Golden Dome defense contract, Neutron 2026',
    },
    'ASTS': {
        'output_files': ['output/2026-05-07_ASTS_analysis.md', 'output/2026-05-09_space_industry_analysis.md', 'output/2026-05-13_ASTS_SOFI_analysis.md'],
        'sources_txt': ['tools/ASTS_sources.txt', 'tools/ASTS_may13_sources.txt'],
        'session': '2026-05-07 + 05-09 + 05-13',
        'company': 'AST SpaceMobile',
        'thesis_one_liner': 'Direct-to-device satellite internet (BlueBird constellation) — watchlist: ราคาแพง P/S 411x',
    },
    'SOFI': {
        'output_files': ['output/2026-05-06_SOFI_analysis.md', 'output/2026-05-08_SOFI_analysis.md', 'output/2026-05-13_ASTS_SOFI_analysis.md'],
        'sources_txt': ['tools/SOFI_sources.txt'],
        'session': '2026-05-06 + 05-08 + 05-13',
        'company': 'SoFi Technologies',
        'thesis_one_liner': 'One-stop fintech bank challenger — risk: Muddy Waters short (11 Qs unanswered), MW short 13%',
    },
    'NVO': {
        'output_files': ['output/2026-05-06_NVO_analysis.md'],
        'sources_txt': ['tools/NVO_sources.txt'],
        'session': '2026-05-06',
        'company': 'Novo Nordisk ADR',
        'thesis_one_liner': 'GLP-1 obesity drug leader (Wegovy/Ozempic) — risk: CagriSema failure, Medicare pricing',
    },
    'UNH': {
        'output_files': ['output/2026-05-08_UNH_analysis.md'],
        'sources_txt': ['tools/UNH_sources.txt'],
        'session': '2026-05-08',
        'company': 'UnitedHealth Group',
        'thesis_one_liner': 'Largest US health insurer — risk: DOJ criminal probe, MLR expansion, ราคาเกิน analyst PT',
    },
    'GOOGL': {
        'output_files': ['output/2026-05-14_GOOGL_analysis.md'],
        'sources_txt': ['tools/GOOGL_sources.txt'],
        'session': '2026-05-14',
        'company': 'Alphabet (Google)',
        'thesis_one_liner': 'Search/Cloud/AI dominance (Gemini), Waymo optionality — risk: DOJ antitrust Chrome divestiture',
    },
    'AMZN': {
        'output_files': ['output/2026-05-08_AMZN_analysis.md'],
        'sources_txt': ['tools/AMZN_sources.txt'],
        'session': '2026-05-08',
        'company': 'Amazon',
        'thesis_one_liner': 'AWS cloud + ecommerce flywheel — risk: CapEx surge kills FCF 2025-26',
    },
    'PLTR': {
        'output_files': ['output/2026-05-11_portfolio_full_analysis.md', 'output/2026-05-13_portfolio_analysis.md'],
        'sources_txt': ['tools/PLTR_sources.txt'],
        'session': '2026-05-11',
        'company': 'Palantir Technologies',
        'thesis_one_liner': 'AI/data platform for government + enterprise (AIP) — risk: P/S >100x, valuation extreme',
    },
}


os.makedirs('Database/sources', exist_ok=True)

def run_build_pages():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Build Database/sources/{TICKER}.md dedicated source page")
    parser.add_argument("--ticker", help="Ticker symbol")
    parser.add_argument("--sources-txt", help="Path to sources txt file")
    parser.add_argument("--output-file", help="Path to generated report file")
    parser.add_argument("--session", help="Session description")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--thesis", help="Thesis one-liner")
    args = parser.parse_args()

    if args.ticker and args.sources_txt and args.output_file:
        ticker_upper = args.ticker.upper()
        # Find default company name and thesis
        company = args.company or f"{ticker_upper} Corporation"
        thesis = args.thesis or f"Long-term DCA investment target — risk: macroeconomic and business-specific constraints"
        configs_to_run = {
            ticker_upper: {
                'output_files': [args.output_file],
                'sources_txt': [args.sources_txt],
                'session': args.session or f"DCA Assessment {datetime.now().strftime('%Y-%m-%d')}",
                'company': company,
                'thesis_one_liner': thesis
            }
        }
    else:
        configs_to_run = configs

    for ticker, cfg in configs_to_run.items():
        desc_map = extract_link_descriptions(cfg['output_files'])

        all_urls = []
        for sf in cfg['sources_txt']:
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_urls.extend(url_pattern.findall(content))
            except:
                pass
        all_urls = list(dict.fromkeys(all_urls))

        # Build page
        date_str = datetime.now().strftime("%Y-%m-%d")
        lines = []
        lines.append(f'# 📎 {ticker} — Research Sources')
        lines.append(f'> **Company:** {cfg["company"]}  ')
        lines.append(f'> **Thesis:** {cfg["thesis_one_liner"]}  ')
        lines.append(f'> **Research Sessions:** {cfg["session"]} | **Updated:** {date_str}  ')
        lines.append(f'> **Total Sources:** {len(all_urls)}')
        lines.append('')
        lines.append('> 💡 **วิธีใช้:** อ่านหน้านี้แทนการเปิด URL — summary บอกว่าแต่ละ source พูดถึงอะไรและเกี่ยวกับ thesis ยังไง')
        lines.append('')
        lines.append('---')
        lines.append('')

        # Group by tag category
        categories = {
            '#IR': ('📋 Official IR & Earnings Releases', []),
            '#earnings': ('📊 Earnings & Financial Data', []),
            '#analyst': ('🎯 Analyst Coverage & Price Targets', []),
            '#valuation': ('💰 Valuation & Financial Metrics', []),
            '#risk': ('⚠️ Risk Factors & Short Reports', []),
            '#moat': ('🏰 Competitive Moat & Market Position', []),
            '#sector': ('🌐 Sector & Industry Analysis', []),
            '#product': ('🚀 Product & Catalyst News', []),
            '#catalyst': ('⚡ Contracts & M&A Catalysts', []),
            '#macro': ('🌍 Macro & Regulatory Environment', []),
            '#smartmoney': ('🦅 Smart Money & Institutional', []),
            '#technicals': ('📈 Technical Analysis', []),
            '#youtube': ('🎬 YouTube Sources', []),
            '#news': ('📰 News & General Coverage', []),
        }

        url_done = set()
        for url in all_urls:
            desc = desc_map.get(url, '')
            if not desc:
                for ku, kd in desc_map.items():
                    if url[:55] in ku or ku[:55] in url:
                        desc = kd
                        break

            # Get summary from KNOWN_SUMMARIES
            summary = ''
            for key, val in KNOWN_SUMMARIES.items():
                if key in url:
                    summary = val
                    break

            tags = get_tags(url, desc)
            tag_list = tags.split()

            # Find primary category
            primary_cat = '#news'
            priority = ['#IR', '#earnings', '#analyst', '#valuation', '#risk', '#moat', '#sector', '#product', '#catalyst', '#macro', '#smartmoney', '#technicals', '#youtube', '#news']
            for p in priority:
                if p in tag_list:
                    primary_cat = p
                    break

            title = desc if desc else url.split('/')[2].replace('www.', '')
            entry = (title, tags, summary, url)
            if url not in url_done:
                categories[primary_cat][1].append(entry)
                url_done.add(url)

        for cat_tag, (cat_title, entries) in categories.items():
            if not entries:
                continue
            lines.append(f'## {cat_title}')
            lines.append('')
            for title, tags, summary, url in entries:
                lines.append(f'### {title}')
                lines.append(f'**Tags:** {tags}  ')
                if summary:
                    lines.append(f'**สรุป:** {summary}  ')
                lines.append(f'**URL:** {url}')
                lines.append('')
            lines.append('---')
            lines.append('')

        page_content = '\n'.join(lines)
        out_path = f'Database/sources/{ticker}.md'
        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f'{ticker}: {len(all_urls)} sources -> {out_path}')
        except Exception as e:
            print(f'[-] Failed to write source page for {ticker}: {e}')

if __name__ == "__main__":
    run_build_pages()

