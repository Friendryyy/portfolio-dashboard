import os
import re
from urllib.parse import urlparse

# Strict URL-to-Summary mapping to avoid domain-level mismatches
EXACT_SUMMARIES = {
    # SOFI
    "https://muddywatersresearch.com/research/2026/mw-short-0317/": "รายงาน Short Report ของ Muddy Waters (17/03/2026) กล่าวหาระบบบัญชีของ SoFi เรื่องความโปร่งใสและมูลค่าสินทรัพย์หลักทรัพย์ — เป็นแหล่งข้อมูลหลักของ Thesis Breaker",
    "https://muddywatersresearch.com/wp-content/uploads/2026/03/MWR_20260317.pdf": "รายงาน Short Report ฉบับเต็ม (PDF) จาก Muddy Waters วิเคราะห์ 11 คำถามที่ยังไม่มีคำตอบเกี่ยวกับบัญชีหลักทรัพย์และการประเมินมูลค่าเงินกู้ของ SoFi",
    "https://muddywatersresearch.com/research/2026/sofi-11-questions/": "รายชื่อคำถาม 11 ข้อของ Muddy Waters เกี่ยวกับระบบบัญชีและโครงสร้างเงินทุนของ SoFi ซึ่ง SoFi ยังไม่ได้ตอบอย่างครบถ้วน",
    "https://investors.sofi.com/news/news-details/2026/SoFi-Responds-to-Inaccurate-Short-Seller-Report/default.aspx": "เอกสารชี้แจงและตอบโต้ฉบับอย่างเป็นทางการจากฝ่ายนักลงทุนสัมพันธ์ของ SoFi ปฏิเสธข้อกล่าวหาของ Muddy Waters ว่าไม่ถูกต้องและคลาดเคลื่อน",
    "https://fortune.com/2026/03/25/muddy-waters-sofi-stock-accounting/": "บทวิเคราะห์จาก Fortune สรุปประเด็นข้อพิพาททางบัญชีและการต่อสู้ด้านความเชื่อมั่นระหว่าง Muddy Waters และ SoFi หลังการออกรายงาน Short Report",
    "https://investors.sofi.com/financials/quarterly-results/default.aspx": "หน้าหลักฝ่ายนักลงทุนสัมพันธ์ของ SoFi สำหรับรายงานงบการเงินไตรมาสและผลการดำเนินงานอย่างเป็นทางการ",
    "https://www.investing.com/news/company-news/sofi-q1-2026-slides-41-revenue-growth-stock-drops-on-concerns-93CH-4645538": "สรุปสไลด์ผลประกอบการ Q1 2026 ของ SoFi เติบโต 41% แต่ราคาหุ้นตกลงจากความกังวลเรื่องการเติบโตของเงินกู้และความสามารถในการทำกำไร",
    "https://www.tikr.com/blog/sofi-stock-dropped-14-after-record-earnings-heres-what-comes-next-in-2026": "บทความวิเคราะห์เจาะลึกสาเหตุที่ราคาหุ้น SoFi ร่วงลง 14% หลังการรายงานงบการเงินที่ดีเป็นประวัติการณ์ และแนวโน้มพฤติกรรมราคาในปี 2026",
    "https://finance.yahoo.com/markets/stocks/articles/sofi-technologies-inc-q1-2026-164724498.html": "การสรุปประเด็นสำคัญจาก Earnings Call ของ SoFi ประจำไตรมาส Q1 2026 และความกังวลของนักลงทุนต่อการรักษาระดับการเติบโต",
    "https://stockstory.org/us/stocks/nasdaq/sofi/news/earnings-call/sofi-q1-2026-deep-dive-loan-growth-and-product-expansion-amidst-investor-caution": "การวิเคราะห์เชิงลึกของงบ Q1 2026 เน้นการเติบโตของวงเงินกู้และการขยายตัวของเทคโนโลยีแพลตฟอร์ม (Galileo) ท่ามกลางความระมัดระวังของนักลงทุน",
    "https://s27.q4cdn.com/749715820/files/doc_financials/2026/q1/2026-Q1-Earnings-Release_FINAL.pdf": "รายงานผลประกอบการไตรมาส Q1 2026 ฉบับทางการ (PDF) ของ SoFi แสดงตัวเลขรายได้รวม กำไรสุทธิ และจำนวนสมาชิกที่เพิ่มขึ้น",
    "https://www.investing.com/news/transcripts/earnings-call-transcript-sofi-technologies-q1-2026-sees-revenue-growth-stock-dips-93CH-4645289": "บทสัมภาษณ์และบทถอดเทป Earnings Call ฉบับเต็มสำหรับ Q1 2026 ชี้แจงมุมมองของผู้บริหารต่อแนวโน้มอัตราดอกเบี้ยและพอร์ตสินเชื่อ",
    "https://www.coindesk.com/business/2026/05/07/sofi-s-relaunched-crypto-business-generated-usd121-6-million-in-q1-transaction-revenue": "รายงาน SoFi กลับมารุกธุรกิจ Crypto อีกครั้งและสามารถสร้างรายได้ค่าธรรมเนียมธุรกรรมกว่า $121.6 ล้านดอลลาร์ในไตรมาสแรกของปี 2026",
    "https://www.galileo-ft.com/news/engagement-new-partnerships-drive-growth-for-sofi-tech-platform-in-q3/": "พันธมิตรและการรวมตัวทางเทคโนโลยีใหม่ๆ ของ Galileo ซึ่งช่วยสนับสนุนให้เกิดการเติบโตของเทคโนโลยีแพลตฟอร์มที่เป็น Moat สำคัญของ SoFi",
    "https://investors.sofi.com/news/news-details/2025/SoFi-Launches-Fully-Reserved-Stablecoin-to-Power-Financial-Infrastructure-for-Banks-Fintechs-and-Enterprise-Partners/default.aspx": "SoFi ประกาศเปิดตัวโครงสร้างพื้นฐานเหรียญ Stablecoin (SoFiUSD) หนุนการทำธุรกรรมแบบ B2B สำหรับสถาบันการเงินและองค์กรพันธมิตร",
    "https://www.ainvest.com/news/sofi-credit-quality-growth-strategy-fintech-titan-path-long-term-profitability-2507/": "การวิเคราะห์คุณภาพสินเชื่อและพอร์ตความเสี่ยงของ SoFi และการเดินหน้าตามยุทธศาสตร์เพื่อให้ได้กำไรที่ยั่งยืนในฐานะยักษ์ใหญ่ฟินเทค",
    "https://www.cnbc.com/2026/04/29/sofi-ceo-defends-decision-to-hold-guidance-steady.html": "ผู้บริหารสูงสุด Anthony Noto ออกโรงแถลงป้องกันแนวคิดการคงประมาณการทั้งปีไว้ตามเดิม เพื่อรักษาวินัยทางการเงินและสะท้อนความจริงอย่างจริงใจ",
    "https://247wallst.com/investing/2026/04/29/sofi-slides-9-after-q1-earnings-is-the-sell-on-beat-pattern-repeating-again/": "วิเคราะห์การปรับตัวร่วงลง 9% ของราคาหุ้น SoFi หลังการประกาศงบ สะท้อนรูปแบบการเก็งกำไรในอดีต (Sell on Beat)",
    "https://247wallst.com/investing/2026/05/12/truist-cuts-sofi-price-target-to-17-loan-platform-slowdown-pressures-the-bull-case/": "Truist ปรับลดราคาเป้าหมายของ SoFi ลงเหลือ $17 เนื่องจากเห็นสัญญาณชะลอตัวในแพลตฟอร์มการปล่อยสินเชื่อที่กดดันกรณีการเติบโตแบบก้าวกระโดด",
    
    # RKLB
    "https://www.stocktitan.net/news/RKLB/rocket-lab-announces-first-quarter-2026-financial-results-surpasses-cznv7fzbueb0.html": "เอกสารแถลงอย่างเป็นทางการของ Rocket Lab ไตรมาส Q1 2026 ชี้ว่ารายได้ทำลายสถิติสูงสุดและยืนยัน Neutron launch timeline ในปี 2026",
    "https://www.stocktitan.net/news/RKLB/rocket-lab-to-acquire-robotics-leader-motiv-space-d4u8iu14p9zb.html": "Rocket Lab ประกาศแผนควบรวมกิจการ Motiv Space Systems (ผู้นำระบบหุ่นยนต์อวกาศ) เพื่อขยายความสามารถกลุ่ม Space Systems",
    "https://www.investing.com/news/company-news/rocket-lab-q1-2026-slides-record-revenue-up-64-backlog-hits-22b-93CH-4671036": "ภาพสไลด์ Q1 2026 แสดงรายได้เติบโต 64% และยอด Backlog สั่งซื้อสะสมมูลค่าสูงถึง $2.2 พันล้านดอลลาร์ เพื่อยืนยันความต้องการระยะยาว",
    "https://rocketlabcorp.com/updates/rocket-lab-awarded-816m-prime-contract-to-build-missile-defense-satellite-constellation-for-u-s-space-force/": "Rocket Lab ชนะการประมูลสัญญามูลค่า $816 ล้านดอลลาร์จากกองทัพอวกาศสหรัฐฯ (US Space Force) ในฐานะ Prime Contractor สำหรับโครงการป้องกันภัยดาวเทียม",
    "https://www.fool.com/investing/2026/05/02/why-rocket-lab-stock-zoomed-285-higher-in-april/": "บทวิเคราะห์จาก Motley Fool ระบุปัจจัยที่หนุนหุ้น RKLB เพิ่มขึ้น 28.5% ในเดือนเมษายน จากผลบวกของการคว้าสัญญาทหารและการเตรียมพร้อม Neutron",
    "https://www.fool.com/investing/how-to-invest/stocks/rocket-lab-stock-forecast/": "การวิเคราะห์คาดการณ์ระยะยาวของ Rocket Lab และความแข็งแกร่งของกลไกจัดซื้อในฐานะบริษัทอวกาศครบวงจร",
    "https://www.bloomberg.com/news/articles/2026-05-07/rocket-lab-rises-on-strong-sales-with-neutron-on-track-2026": "Bloomberg รายงานสเตตัส Neutron จรวดขนาดกลางของ Rocket Lab ยืนยันกำหนดการปล่อยในปี 2026 และยอดขายที่เอาชนะประมาณการของตลาด",
    "https://seekingalpha.com/article/4897959-rocket-lab-stock-setting-up-for-growth-ahead-of-q1-2026-earnings": "บทวิเคราะห์ก่อนรายงานงบ Q1 2026 ของ Seeking Alpha แสดงความแข็งแกร่งและโอกาสที่จะเกิด Growth Catalyst ในพอร์ต Space Systems",
    "https://csps.aerospace.org/papers/fy-2026-defense-space-budget-emergence-golden-dome": "รายงานจาก Aerospace Corporation วิเคราะห์งบประมาณด้านอวกาศและการป้องกันประเทศประจำปี 2026 และความมั่นคงของสัญญากองทัพ",
    "https://orbital-intel.com/spacex-vs-rocket-lab/": "การเปรียบเทียบการแข่งขันระหว่าง SpaceX และ Rocket Lab ทั้งในด้านโครงสร้างต้นทุนจรวดและความก้าวหน้าของ Neutron",
    "https://www.tipranks.com/news/rklb-asts-lunr-morgan-stanley-turns-bullish-on-space-stocks": "Morgan Stanley ปรับมุมมองอุตสาหกรรมขึ้นเป็น Bullish สำหรับหุ้นอวกาศ (RKLB, ASTS, LUNR) เนื่องจากการเติบโตของโครงสร้างพื้นฐานเชิงพาณิชย์",
    "https://www.airandspaceforces.com/space-force-reveals-space-based-interceptor-awards-golden-dome/": "กองทัพอวกาศสหรัฐเผยรายละเอียดโครงการดักจับวัตถุและป้องกันภัยทางอวกาศ (Golden Dome) ยืนยันบทบาทผู้รับเหมาหลักของ Rocket Lab",
    "https://www.airandspaceforces.com/space-force-spending-could-hit-40b-in-2026/": "งบประมาณจัดซื้อและพัฒนาเทคโนโลยีของกองทัพอวกาศสหรัฐฯ มีแนวโน้มพุ่งสูงถึง $4.0 หมื่นล้านดอลลาร์ในปี 2026 หนุนมูลค่าตลาด RKLB",
    
    # ASTS
    "https://www.cnbc.com/2026/04/20/ast-falls-after-blue-origin-puts-broadband-satellite-into-wrong-orbit.html": "CNBC รายงานข่าวความผิดพลาดในการส่งดาวเทียม BlueBird 7 ขึ้นสู่วงโคจรที่ผิดพลาดโดย Blue Origin ส่งผลให้หุ้น ASTS ปรับฐานรุนแรง",
    "https://satnews.com/2026/05/07/ast-spacemobile-secures-spacex-launch-contract-for-june-flight/": "ASTS บรรลุข้อตกลงและเปลี่ยนแผนมาใช้ SpaceX ในการขนส่งดาวเทียม BlueBird รอบถัดไปในกลางเดือนมิถุนายน เพื่อแก้ปัญหาวงโคจรผิดพลาด",
    "https://www.fool.com/earnings/call-transcripts/2026/05/11/ast-spacemobile-inc-asts-q1-2026-earnings-call-transcript/": "บทถอดเสียงโทรศัพท์งบการเงินไตรมาส Q1 2026 ของ ASTS ยืนยันเป้าหมายส่งมอบดาวเทียม BlueBirds จำนวน 45 ดวงภายในสิ้นปี 2026",
    
    # NVDA
    "https://www.tomshardware.com/tech-industry/artificial-intelligence/jensen-says-nvidia-now-has-zero-percent-market-share-in-china-says-us-export-policy-has-already-largely-backfired": "รายงานบทสัมภาษณ์ Jensen Huang ชี้แจงว่าส่วนแบ่งตลาดของชิป AI ในจีนลดลงเหลือเกือบ 0% จากข้อห้ามส่งออกของสหรัฐฯ ชี้ส่งผลสะท้อนกลับเชิงลบ",
    "https://futurumgroup.com/insights/nvidia-q3-fy-2026-record-data-center-revenue-higher-q4-guide/": "บทวิเคราะห์จาก Futurum Research สรุปรายงานรายได้ Q3 FY2026 นำโดยตัวเลข Data Center และเป้าหมายรายได้ Blackwell ประจำไตรมาสถัดไป",
    "https://www.foreignpolicyjournal.com/2026/04/26/nvidia-nvda-stock-rating-raised-to-buy-as-export-controls-and-ai-demand-set-up-strong-second-half/": "นักวิเคราะห์ปรับเรตติ้งของ NVIDIA ขึ้นเป็น BUY ระบุว่าการจัดวางชิป Blackwell ไปยังภูมิภาคยุโรปและสหรัฐช่วยชดเชยการลดส่งออกไปยังจีน",
    "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026": "การประกาศงบการเงินปีงบประมาณ 2026 ของ NVIDIA อย่างเป็นทางการ รายได้รวมโต 68% แตะระดับสูงสุดเป็นประวัติการณ์",
    
    # GOOGL
    "https://io.google/2026/": "งานเปิดตัวนวัตกรรมประจำปี Google I/O 2026 แสดงทักษะ AI ล่าสุดของ Gemini 2.5, การฝัง AI ใน Android XR และอนาคตของ Search",
    
    # AMZN
    "https://247wallst.com/investing/2026/05/05/amazons-free-cash-flow-plummets-26b-to-1-2b-capex-surge/": "การวิเคราะห์วิกฤตกระแสเงินสดอิสระ (FCF) ของ Amazon ปรับตัวลดลงจาก $2.6 หมื่นล้านเหลือเพียง $1.2 พันล้านดอลลาร์อันเนื่องมาจากการโหมลงทุนสร้างดาต้าเซ็นเตอร์ AI",
}

# Domain mapping patterns to fall back on in Thai but restricted to generic information
DOMAIN_SUMMARIES = {
    "sec.gov": "เอกสารรายงานหรือคำชี้แจงทางการเงินที่ยื่นต่อสำนักงานคณะกรรมการกำกับหลักทรัพย์และตลาดหลักทรัพย์ของสหรัฐฯ (SEC) เพื่อการตรวจสอบแบบเป็นสถาบัน",
    "fool.com": "บทวิเคราะห์และความคิดเห็นทางการเงินเชิงลึกระยะยาวจากทีมงาน The Motley Fool ช่วยเปรียบเทียบแนวโน้มหุ้นกับดัชนีภาพรวม",
    "seekingalpha.com": "บทความวิเคราะห์วิจัยเชิงปริมาณและมุมมองของนักลงทุนอิสระและมืออาชีพบนแพลตฟอร์ม Seeking Alpha คาดการณ์ผลประกอบการล่วงหน้า",
    "investors.sofi.com": "ข้อมูลชี้แจง ทิศทางองค์กร และผลประกอบการสำหรับนักลงทุนจัดทำโดยฝ่ายนักลงทุนสัมพันธ์ของ SoFi Technologies",
    "yfinance": "ข้อมูลราคาหุ้น ตัวคูณมูลค่า พื้นฐานการเงิน และประมาณการฉันทามติของนักวิเคราะห์จาก Yahoo Finance",
    "twelvedata.com": "ข้อมูลดิบด้านดัชนีราคาหุ้นและการวิเคราะห์ปัจจัยทางเทคนิค (เช่น RSI, MACD, Bollinger Bands) ดึงผ่าน Twelve Data API",
    "youtube.com": "การบรรยายสรุปเชิงลึก มุมมองนักลงทุนอิสระ หรือการสัมภาษณ์ผู้บริหารผ่านช่องรายการและคลิปวิดีโอบนยูทูป",
}

def extract_all_links_from_vault():
    """
    Scans all .md files under database/stocks/, database/sectors/, and output/
    to build a robust global mapping of URL -> (descriptive label, surrounding context/paragraphs).
    """
    url_to_info = {}
    link_regex = re.compile(r'\[([^\]]+)\]\((https?://[^\s\)\>]+)\)')
    
    scan_paths = [
        "database/stocks",
        "database/sectors",
        "output"
    ]
    
    for folder in scan_paths:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                if not file.endswith(".md"):
                    continue
                fp = os.path.join(root, file)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        for match in link_regex.finditer(line):
                            label, url = match.group(1).strip(), match.group(2).strip()
                            # Clean up labels starting with URL or generic domain strings
                            if len(label) <= 3 or label.startswith("http") or "www." in label:
                                continue
                            
                            # Find surrounding context
                            context_lines = []
                            # Look back 1 line
                            if i > 0 and lines[i-1].strip():
                                context_lines.append(lines[i-1].strip())
                            # Add current line
                            context_lines.append(line.strip())
                            # Look ahead 1 line
                            if i < len(lines) - 1 and lines[i+1].strip():
                                context_lines.append(lines[i+1].strip())
                                
                            combined_context = " | ".join(context_lines)
                            # Remove excessive markdown syntax from context
                            combined_context = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', combined_context)
                            combined_context = combined_context.replace("*", "").replace("#", "").strip()
                            if len(combined_context) > 250:
                                combined_context = combined_context[:250] + "..."
                                
                            if url not in url_to_info:
                                url_to_info[url] = {
                                    "labels": set(),
                                    "contexts": set()
                                }
                            url_to_info[url]["labels"].add(label)
                            if len(combined_context) > 20:
                                url_to_info[url]["contexts"].add(combined_context)
                except Exception as e:
                    print(f"Error parsing file {fp}: {e}")
                    
    # Simplify sets to single strings
    simplified_map = {}
    for url, info in url_to_info.items():
        # Pick the longest label that doesn't look like a URL
        best_label = ""
        for lbl in info["labels"]:
            if len(lbl) > len(best_label) and not lbl.startswith("http"):
                best_label = lbl
        
        # Pick best context
        best_context = ""
        for ctx in info["contexts"]:
            if len(ctx) > len(best_context) and len(ctx) > 30:
                best_context = ctx
                
        simplified_map[url] = {
            "label": best_label,
            "context": best_context
        }
    return simplified_map

def distill_source_pages(vault_links):
    """
    Scans every existing file in Database/sources/*.md, parses its current URLs,
    updates summaries with exact matches, contextual extracts, or clean domain-level descriptions,
    and saves the file back in perfect Distilled Source Protocol format.
    """
    sources_dir = "database/sources"
    if not os.path.exists(sources_dir):
        print(f"Sources directory not found: {sources_dir}")
        return
        
    source_files = [f for f in os.listdir(sources_dir) if f.endswith(".md")]
    
    url_regex = re.compile(r'\*\*URL:\*\*\s*(https?://[^\s\)]+)')
    tag_regex = re.compile(r'\*\*Tags:\*\*\s*(#[^\n]+)')
    title_regex = re.compile(r'###\s+([^\n]+)')
    
    for sf in source_files:
        fp = os.path.join(sources_dir, sf)
        print(f"Processing sources file: {sf}")
        
        try:
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
                
            # We want to parse sections and rebuild them cleanly
            # Split file by '---'
            parts = content.split("---")
            header = parts[0]
            footer_lines = []
            
            # Rebuild components
            new_parts = [header]
            
            for part in parts[1:]:
                # Each part contains several sources separated by blank lines or paragraphs
                # Let's split by '###'
                subparts = part.split("###")
                part_header = subparts[0]
                new_part_content = [part_header]
                
                for entry in subparts[1:]:
                    lines = entry.strip().split("\n")
                    title = lines[0].strip()
                    tags = ""
                    url = ""
                    old_summary = ""
                    
                    for line in lines[1:]:
                        line_strip = line.strip()
                        if line_strip.startswith("**Tags:**"):
                            tags = line_strip.replace("**Tags:**", "").strip()
                        elif line_strip.startswith("**URL:**"):
                            url = line_strip.replace("**URL:**", "").strip()
                        elif line_strip.startswith("**สรุป:**"):
                            old_summary = line_strip.replace("**สรุป:**", "").strip()
                            
                    # Clean up url
                    url = url.strip()
                    
                    # Distill summary determination
                    distilled_summary = ""
                    
                    # 1. Check exact summaries list
                    if url in EXACT_SUMMARIES:
                        distilled_summary = EXACT_SUMMARIES[url]
                    else:
                        # Find matches that are subsets of the exact mapping to be safe
                        for key, val in EXACT_SUMMARIES.items():
                            if url[:65] in key or key[:65] in url:
                                distilled_summary = val
                                break
                                
                    # 2. Check extracted vault contexts
                    if not distilled_summary and url in vault_links:
                        v_info = vault_links[url]
                        if v_info["context"]:
                            # Use context as summary if it is solid
                            distilled_summary = f"ข้อมูลประกอบการศึกษา: {v_info['context']}"
                        if v_info["label"] and len(v_info["label"]) > 10 and len(title) < len(v_info["label"]):
                            title = v_info["label"]
                            
                    # 3. Fall back on generic domain explanations if no specific summary is found
                    if not distilled_summary:
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc.replace("www.", "")
                        
                        # Look for domain keys
                        found_domain = False
                        for dom_key, dom_desc in DOMAIN_SUMMARIES.items():
                            if dom_key in domain:
                                distilled_summary = dom_desc
                                found_domain = True
                                break
                        
                        if not found_domain:
                            # Default clean domain explanation
                            distilled_summary = f"แหล่งข่าวสารหรือการรายงานความคืบหน้าของอุตสาหกรรมทางการเงินจากเว็บไซต์ {domain}"
                            
                    # Let's ensure the title is neat
                    if not title or title.startswith("http"):
                        parsed_url = urlparse(url)
                        title = parsed_url.netloc.replace("www.", "")
                        
                    # Reconstruct source entry in markdown
                    entry_md = f"### {title}\n"
                    if tags:
                        entry_md += f"**Tags:** {tags}  \n"
                    else:
                        entry_md += f"**Tags:** #news  \n"
                    
                    entry_md += f"**สรุป:** {distilled_summary}  \n"
                    entry_md += f"**URL:** {url}\n"
                    
                    new_part_content.append(entry_md)
                
                # Join source entries back together
                rebuilt_part = "\n".join(new_part_content)
                new_parts.append(rebuilt_part)
                
            # Reconstruct the entire file
            rebuilt_file = "---".join(new_parts)
            
            # Save it back!
            with open(fp, "w", encoding="utf-8") as f:
                f.write(rebuilt_file)
            print(f"Successfully distilled and saved: {sf}")
            
        except Exception as e:
            print(f"Error processing source file {sf}: {e}")

if __name__ == "__main__":
    print("[Phase 1] Scanning vault for links & contexts...")
    vault_links = extract_all_links_from_vault()
    print(f"Parsed {len(vault_links)} unique links with context.")
    
    print("\n[Phase 2] Applying Distilled Source Protocol to Database/sources/ files...")
    distill_source_pages(vault_links)
    print("\nDistillation complete! Every source in the vault is now highly readable and descriptive.")
