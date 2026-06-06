import re

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
    url_lower = url.lower()
    desc_lower = desc.lower() if desc else ''
    combined = url_lower + ' ' + desc_lower

    if 'youtube.com' in url_lower: tags.append('#youtube')
    if 'sec.gov' in url_lower: tags.append('#sec')
    if any(x in combined for x in ['investor.', '/ir/', 'investor-relations', 'newsroom', 'news-release', 'quarterly-results', 'financial-results', 'abc.xyz']): tags.append('#IR')
    if any(x in combined for x in ['earnings', 'q1 ', 'q2 ', 'q3 ', 'q4 ', 'revenue', 'eps', 'guidance', 'transcript', 'results']): tags.append('#earnings')
    if any(x in combined for x in ['valuation', 'p/e', 'dcf', 'pe ratio', 'fair value', 'price target', 'forward pe', 'statistics', 'macrotrends', 'gurufocus', 'alphaspread']): tags.append('#valuation')
    if any(x in combined for x in ['analyst', 'rating', 'upgrade', 'downgrade', 'price target', 'raised to buy', 'bull', 'forecast', 'target']): tags.append('#analyst')
    if any(x in combined for x in ['risk', 'short', 'muddy waters', 'concern', 'probe', 'doj', 'antitrust', 'regulation', 'fda', 'export control', 'china', 'zero market share', 'charge', 'investigation']): tags.append('#risk')
    if any(x in combined for x in ['moat', 'competitive', 'market share', 'advantage', 'competitor', ' vs ', 'peer', 'cuda', 'ecosystem']): tags.append('#moat')
    if any(x in combined for x in ['macro', 'fed', 'rate', 'inflation', 'gdp', 'geopolit', 'war', 'tariff', 'policy', 'iran', 'taiwan', 'israel', 'trump', 'xi']): tags.append('#macro')
    if any(x in combined for x in ['insider', '13f', 'institutional', 'holder', 'ownership', 'smart money', 'fintel', 'short interest']): tags.append('#smartmoney')
    if any(x in combined for x in ['sector', 'industry', 'market size', 'tam', 'space', 'satellite', 'defense', 'glp-1', 'obesity', 'ai chip', 'fintech', 'cloud', 'semiconductor', 'golden dome', 'launch']): tags.append('#sector')
    if any(x in combined for x in ['technical', 'rsi', 'macd', 'support', 'resistance', 'chart']): tags.append('#technicals')
    if any(x in combined for x in ['acqui', 'merger', 'deal', 'contract', 'award', 'partnership', 'motiv', 'anduril']): tags.append('#catalyst')
    if any(x in combined for x in ['waymo', 'gemini', 'deepmind', 'ai model', 'product', 'i/o', 'blackwell', 'neutron', 'bluebird', 'wegovy', 'ozempic', 'semaglutide', 'prime', 'aip', 'gotham', 'foundry']): tags.append('#product')
    if any(x in combined for x in ['stockanalysis', 'stocktwits', 'seekingalpha', 'fool.com', 'benzinga', 'marketbeat', '247wallst', 'investing.com', 'bloomberg', 'cnbc', 'reuters', 'wsj', 'fortune', 'coindesk']): tags.append('#news')
    if 'youtube.com' not in url_lower and not tags: tags.append('#news')
    return ' '.join(sorted(set(tags)))

# Config for each ticker
configs = {
    'NVDA': {
        'output_files': ['output/2026-05-06_NVDA_analysis.md'],
        'sources_txt': ['tools/NVDA_sources.txt'],
        'session': '2026-05-06 Full 13-Agent Analysis',
    },
    'RKLB': {
        'output_files': ['output/2026-05-08_RKLB_monitoring_update.md', 'output/2026-05-09_RKLB_monitoring_update.md', 'output/2026-05-09_space_industry_analysis.md'],
        'sources_txt': ['tools/RKLB_sources.txt'],
        'session': '2026-05-09 Q1 Earnings + Space Sector',
    },
    'ASTS': {
        'output_files': ['output/2026-05-07_ASTS_analysis.md', 'output/2026-05-09_space_industry_analysis.md', 'output/2026-05-13_ASTS_SOFI_analysis.md'],
        'sources_txt': ['tools/ASTS_sources.txt', 'tools/ASTS_may13_sources.txt'],
        'session': '2026-05-09 Sector + 2026-05-13 Q1 Earnings',
    },
    'SOFI': {
        'output_files': ['output/2026-05-06_SOFI_analysis.md', 'output/2026-05-08_SOFI_analysis.md', 'output/2026-05-13_ASTS_SOFI_analysis.md'],
        'sources_txt': ['tools/SOFI_sources.txt'],
        'session': '2026-05-06 + 05-08 + 05-13 (3 sessions)',
    },
    'NVO': {
        'output_files': ['output/2026-05-06_NVO_analysis.md'],
        'sources_txt': ['tools/NVO_sources.txt'],
        'session': '2026-05-06 Full 13-Agent Analysis',
    },
    'UNH': {
        'output_files': ['output/2026-05-08_UNH_analysis.md'],
        'sources_txt': ['tools/UNH_sources.txt'],
        'session': '2026-05-08 Full Analysis',
    },
    'GOOGL': {
        'output_files': ['output/2026-05-14_GOOGL_analysis.md'],
        'sources_txt': ['tools/GOOGL_sources.txt'],
        'session': '2026-05-14 Full 13-Agent Deep Dive',
    },
    'AMZN': {
        'output_files': ['output/2026-05-08_AMZN_analysis.md'],
        'sources_txt': ['tools/AMZN_sources.txt'],
        'session': '2026-05-08 Full Analysis',
    },
    'PLTR': {
        'output_files': ['output/2026-05-11_portfolio_full_analysis.md', 'output/2026-05-13_portfolio_analysis.md'],
        'sources_txt': ['tools/PLTR_sources.txt'],
        'session': '2026-05-11 Analysis',
    },
}


url_pattern = re.compile(r'https?://[^\s\)\]\>\"\' ]+')

def run_update():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Update Database/stocks/{TICKER}.md with sources")
    parser.add_argument("--ticker", help="Ticker symbol")
    parser.add_argument("--sources-txt", help="Path to sources txt file")
    parser.add_argument("--output-file", help="Path to generated report file")
    parser.add_argument("--session", help="Session description")
    args = parser.parse_args()

    if args.ticker and args.sources_txt and args.output_file:
        configs_to_run = {
            args.ticker.upper(): {
                'output_files': [args.output_file],
                'sources_txt': [args.sources_txt],
                'session': args.session or f"DCA Assessment {datetime.now().strftime('%Y-%m-%d')}"
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

        date_str = datetime.now().strftime("%Y-%m-%d")
        section = f'\n\n---\n\n## \U0001f4ce Research Sources\n> อัปเดต {date_str} | Sessions: {cfg["session"]}\n\n'
        for url in all_urls:
            desc = desc_map.get(url, '')
            if not desc:
                for known_url, known_desc in desc_map.items():
                    if url[:55] in known_url or known_url[:55] in url:
                        desc = known_desc
                        break
            tags = get_tags(url, desc)
            if desc:
                section += f'- **{desc}** {tags}\n  - {url}\n'
            else:
                domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
                domain_name = domain.group(1) if domain else 'Link'
                section += f'- **{domain_name}** {tags}\n  - {url}\n'

        wiki_path = f'Database/stocks/{ticker}.md'
        try:
            with open(wiki_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if '\U0001f4ce Research Sources' in content:
                idx = content.index('\n\n---\n\n## \U0001f4ce Research Sources')
                content = content[:idx]

            with open(wiki_path, 'w', encoding='utf-8') as f:
                f.write(content.rstrip() + section)

            print(f'{ticker}: {len(all_urls)} URLs with descriptions+tags written to {wiki_path}')
        except Exception as e:
            print(f'[-] Failed to update wiki for {ticker}: {e}')

if __name__ == "__main__":
    run_update()

