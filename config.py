# =============================================================================
# job_radar configuration
# Edit THIS file to add/remove employers, change keywords, and set up email.
# You do not need to touch job_radar.py.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. KEYWORDS  (case-insensitive; substrings count, so "econom" catches
#    economist / economics / econometrics / macroeconomics)
#
#    Each source uses ONE profile:
#      "core"        -> economist-type roles only (institutions, central banks,
#                       tech firms whose boards are mostly engineering).
#      "consultancy" -> also Associate/Consultant/Analyst (at an econ-consulting
#                       firm those ARE the economist roles).
#      "finance"     -> buy/sell-side + rating-agency roles: risk analyst,
#                       fixed-income/rates/macro strategist, quant researcher,
#                       credit analyst, portfolio manager, etc.
#    A job is kept if it matches its profile's INCLUDE list and no EXCLUDE term.
# -----------------------------------------------------------------------------
INCLUDE_CORE = [
    "econom", "monetary", "research economist", "research scientist, econom",
    "policy analyst", "policy economist", "postdoc", "post-doc",
    "research fellow", "quantitative research",
]

INCLUDE_CONSULTANCY = INCLUDE_CORE + [
    "associate", "consultant", "consulting", "principal", "analyst",
    "research assistant",
]

INCLUDE_FINANCE = INCLUDE_CORE + [
    # risk
    "risk analyst", "risk management", "market risk", "credit risk",
    "model risk", "quantitative risk", "risk strategist",
    # strategy / research desks
    "strategist", "macro research", "macro strategist", "rates strategist",
    "investment strategist", "research analyst", "research associate",
    "investment analyst", "investment research",
    # fixed income & rates
    "fixed income", "fixed-income", "rates", "interest rate", "sovereign",
    "credit analyst", "credit research", "structured finance", "securitization",
    "ratings analyst", "rating analyst",
    # quant / portfolio
    "quant research", "quantitative research", "quantitative analyst",
    "quantitative researcher", "quantitative trader", "quantitative strategies",
    "portfolio manager", "portfolio analyst", "asset allocation", "multi-asset",
    "financial economist",
]

EXCLUDE = [
    "intern", "internship", "student", "co-op", "apprentice",
    "administrative assistant", "executive assistant", "receptionist",
    "recruiter", "talent acquisition", "sales", "graphic designer",
    "software engineer", "quantitative developer", "help desk",
    "custodian", "cleaner",
]

# -----------------------------------------------------------------------------
# Geography filter used by the Swiss section. A source carrying "locations"
# keeps only postings whose location matches one of these strings (case-
# insensitive substring). Sources WITHOUT a "locations" key stay unrestricted.
# Geneva/Romandie terms come first, then the rest of Switzerland.
# -----------------------------------------------------------------------------
SWISS_LOCATIONS = [
    # Geneva & French-speaking Switzerland (the priority)
    "geneva", "genève", "geneve", "genf", "carouge", "nyon", "lancy",
    "lausanne", "vaud", "montreux", "vevey", "fribourg", "neuchâtel", "neuchatel",
    # German- & Italian-speaking Switzerland
    "zurich", "zürich", "zug", "baar", "pfäffikon", "pfaffikon", "basel", "basle",
    "bern", "berne", "winterthur", "lucerne", "luzern", "st. gallen", "lugano",
    "schwyz", "vaduz",                     # Vaduz: LGT/Liechtenstein, same market
    # country-level fallbacks (SmartRecruiters renders country as ", ch")
    "switzerland", "suisse", "schweiz", ", ch",
]

# -----------------------------------------------------------------------------
# Geography filter for the London section. Deliberately narrow: bare "uk" is
# NOT used because it also matches "Ukraine". SmartRecruiters renders the
# country as ", gb", Greenhouse/Workday spell out "United Kingdom".
# -----------------------------------------------------------------------------
LONDON_LOCATIONS = [
    "london", "city of london", "canary wharf",
    "united kingdom", "england", ", gb",
]

# -----------------------------------------------------------------------------
# Dashboard freshness. A posting first seen more than this many days ago is
# hidden from the page even if the employer still lists it: after a month it is
# either filled-but-not-removed, or you have already decided against it.
# It stays in seen_jobs.csv, so it is never re-reported as new. Set to 0 to
# show everything again.
# -----------------------------------------------------------------------------
MAX_AGE_DAYS = 30

# Order in which category sections appear on the dashboard.
CATEGORY_ORDER = [
    "Geneva / Swiss private finance",
    "Global macro hedge funds",
    "London private sector",
    "International institutions",
    "Central banks",
    "Rating agencies",
    "Economic consultancies",
    "Buy-side / trading",
    "Sell-side / banks",
    "Private sector / tech",
    "Aggregators (catch-all)",
]

# -----------------------------------------------------------------------------
# 2. SOURCES
#    "type": greenhouse | smartrecruiters | lever | workday | link
#    "profile": "core" (default) | "consultancy" | "finance"
#    "category": one of CATEGORY_ORDER above (groups the dashboard)
#      greenhouse/smartrecruiters/lever -> need "slug"
#      workday   -> need "host","tenant","site"  (deadlines auto-fetched)
#      link      -> no API; a bookmark you open manually ("url")
# -----------------------------------------------------------------------------
SOURCES = [
    # =======================================================================
    #  GENEVA / SWISS PRIVATE FINANCE
    #  Geneva-first, then the rest of Switzerland. Everything here carries
    #  "locations": SWISS_LOCATIONS, so only Swiss postings surface even
    #  though these firms advertise globally.
    #
    #  Reality check: most Geneva private banks and boutique managers run no
    #  public jobs API (several don't even have a stable /careers path), and
    #  much of this market is filled through network and referral rather than
    #  open posting. The three API sources below are the ones that genuinely
    #  resolve; the rest are bookmarks, and the aggregators at the end are
    #  what actually catch the small houses.
    # =======================================================================
    # ---- scraped automatically (verified working) --------------------------
    {"name": "Julius Baer (private bank)", "category": "Geneva / Swiss private finance",
     "type": "workday", "profile": "finance", "locations": SWISS_LOCATIONS,
     "host": "juliusbaer.wd3.myworkdayjobs.com", "tenant": "juliusbaer", "site": "External"},
    {"name": "Vitol (Geneva — commodity trading)", "category": "Geneva / Swiss private finance",
     "type": "smartrecruiters", "slug": "Vitol", "profile": "finance",
     "locations": SWISS_LOCATIONS},
    {"name": "Louis Dreyfus Company (Geneva — commodities)",
     "category": "Geneva / Swiss private finance", "type": "smartrecruiters",
     "slug": "LouisDreyfusCompany", "profile": "finance", "locations": SWISS_LOCATIONS},

    # ---- Geneva private banks (bookmarks — no public API) ------------------
    {"name": "Pictet (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.group.pictet/careers"},
    {"name": "Lombard Odier (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.lombardodier.com/home/careers.html"},
    {"name": "Union Bancaire Privée — UBP (Geneva)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.ubp.com/en/careers"},
    {"name": "Mirabaud (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.mirabaud.com/en/careers"},
    {"name": "Edmond de Rothschild (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.edmond-de-rothschild.com/en/careers"},
    {"name": "Banque SYZ (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.syzgroup.com/en/careers"},
    {"name": "CBH Compagnie Bancaire Helvétique (Geneva)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.cbhbank.com/en/careers"},
    {"name": "Gonet & Cie (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.gonet.ch/en/careers/"},
    {"name": "Piguet Galland (Geneva/Lausanne)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.piguetgalland.ch/en/careers"},
    {"name": "Bordier & Cie (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.bordier.com/"},
    {"name": "REYL Intesa Sanpaolo (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.reyl.com/"},
    {"name": "Bank J. Safra Sarasin (Geneva/Basel)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jsafrasarasin.com/"},
    {"name": "Banque Cramer (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.banquecramer.ch/"},

    # ---- Geneva asset managers / funds / multi-family offices --------------
    {"name": "Unigestion (Geneva — quant multi-asset; strong PhD fit)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.unigestion.com/"},
    {"name": "Quaero Capital (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.quaerocapital.com/"},
    {"name": "Decalia (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://decalia.com/"},
    {"name": "Stonehage Fleming (Geneva — family office)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.stonehagefleming.com/careers"},

    # ---- Zurich / Zug / rest of Switzerland --------------------------------
    {"name": "Vontobel (Zurich)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.vontobel.com/en/careers/"},
    {"name": "EFG International (Zurich/Geneva)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.efginternational.com/"},
    {"name": "GAM Investments (Zurich)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.gam.com/en/careers"},
    {"name": "Bellevue Group (Zurich)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.bellevue.ch/"},
    {"name": "Partners Group (Baar/Zug — private markets)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.partnersgroup.com/en/careers/"},
    {"name": "LGT Capital Partners (Pfäffikon)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.lgt.com/global-en/career"},
    {"name": "Swiss Re (Zurich — has a real economics team)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://careers.swissre.com/"},
    {"name": "Zurich Insurance (Zurich — economics/risk)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.zurich.com/careers"},

    # ---- Geneva commodity trading (macro/fundamental research desks) -------
    #  Geneva is the world's commodity-trading hub; these desks hire macro
    #  economists for supply/demand and price-fundamentals research.
    {"name": "Trafigura (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.trafigura.com/careers/"},
    {"name": "Gunvor (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://gunvorgroup.com/careers/"},
    {"name": "Mercuria (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.mercuria.com/careers"},
    {"name": "COFCO International (Geneva)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.cofcointernational.com/careers/"},
    {"name": "Glencore (Baar)", "category": "Geneva / Swiss private finance",
     "type": "link", "url": "https://www.glencore.com/careers"},

    # ---- Geneva-based, finance-adjacent ------------------------------------
    {"name": "World Economic Forum (Cologny/Geneva — economists)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.weforum.org/about/careers/"},
    {"name": "Swiss Finance Institute (career centre)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.sfi.ch/"},

    # ---- Aggregators: the realistic way to reach the SMALL houses ----------
    #  Boutique Geneva managers rarely run a careers page; when they do post,
    #  it lands on jobup (Romandie's board) or jobs.ch. These searches are the
    #  highest-yield part of this whole section.
    {"name": "jobup.ch — Geneva/Romandie board: 'economist'",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jobup.ch/en/jobs/?term=economist"},
    {"name": "jobup.ch — Geneva: 'analyst' (finance)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jobup.ch/en/jobs/?term=analyst&location=Gen%C3%A8ve"},
    {"name": "jobup.ch — Geneva: 'asset management'",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jobup.ch/en/jobs/?term=asset%20management"},
    {"name": "jobs.ch — Switzerland: 'economist'",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jobs.ch/en/vacancies/?term=economist"},
    {"name": "jobs.ch — Switzerland: 'quantitative research'",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.jobs.ch/en/vacancies/?term=quantitative%20research"},
    {"name": "eFinancialCareers Switzerland (buy-side/private banking)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.efinancialcareers.ch/jobs-Switzerland.s001"},
    {"name": "LinkedIn — Geneva: economist (newest first)",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=economist&location=Geneva%2C%20Switzerland&sortBy=DD"},
    {"name": "LinkedIn — Geneva: quantitative / macro research",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=quantitative%20research%20macro&location=Geneva%2C%20Switzerland&sortBy=DD"},
    {"name": "LinkedIn — Switzerland: portfolio / investment strategist",
     "category": "Geneva / Swiss private finance", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=investment%20strategist&location=Switzerland&sortBy=DD"},

    # =======================================================================
    #  LONDON PRIVATE SECTOR
    #  London is the European hub for macro research, and an LSE/UCL degree
    #  plus IMF/ECB country work reads well there. Everything here carries
    #  "locations": LONDON_LOCATIONS, because all of these firms advertise
    #  globally and only the London desks are relevant.
    #
    #  Reality check, same as Geneva: most of this market has no public jobs
    #  API. Every slug/tenant below was probed and returned real postings for
    #  the right company before being added -- several obvious guesses were
    #  rejected as name collisions (greenhouse "london" is a cafe chain, lever
    #  "capital" is Capital.com, greenhouse "wise" is a US sales agency).
    #  The banks (HSBC, StanChart, Nomura, NatWest, Barclays), the big active
    #  managers (Schroders, M&G, Fidelity Intl) and every pure macro boutique
    #  (Fulcrum, Emso, Exante, Fathom, TS Lombard) run closed boards -> they
    #  are bookmarks at the end of this block.
    #
    #  NOTE ON RUNTIME: Mastercard (~1,100 jobs), Visa (~800) and LSEG (~700)
    #  are large Workday boards, paginated 20 at a time with a pause between
    #  pages. They add roughly 2-3 minutes to the run.
    # =======================================================================
    # ---- scraped automatically (verified working) --------------------------
    {"name": "Capital Economics (London — independent macro research)",
     "category": "London private sector", "type": "workable",
     "slug": "capital-economics", "profile": "core",
     "locations": LONDON_LOCATIONS},
    {"name": "BlueCrest Capital (London — macro/multi-strat)",
     "category": "London private sector", "type": "greenhouse",
     "slug": "bluecrestcapitalmanagement", "profile": "finance",
     "locations": LONDON_LOCATIONS},
    {"name": "Winton (London — systematic macro)",
     "category": "London private sector", "type": "greenhouse",
     "slug": "winton", "profile": "finance", "locations": LONDON_LOCATIONS},
    {"name": "LSEG / FTSE Russell (London — index & data research)",
     "category": "London private sector", "type": "workday", "profile": "finance",
     "locations": LONDON_LOCATIONS,
     "host": "lseg.wd3.myworkdayjobs.com", "tenant": "lseg", "site": "careers"},
    {"name": "Mastercard (London — Economics Institute; fintech chapter fit)",
     "category": "London private sector", "type": "workday", "profile": "finance",
     "locations": LONDON_LOCATIONS,
     "host": "mastercard.wd1.myworkdayjobs.com", "tenant": "mastercard",
     "site": "CorporateCareers"},
    {"name": "Visa (London — Economic Empowerment Institute)",
     "category": "London private sector", "type": "workday", "profile": "finance",
     "locations": LONDON_LOCATIONS,
     "host": "visa.wd5.myworkdayjobs.com", "tenant": "visa", "site": "Visa"},
    {"name": "Legal & General (London — LGIM economics)",
     "category": "London private sector", "type": "smartrecruiters",
     "slug": "legalandgeneral", "profile": "finance",
     "locations": LONDON_LOCATIONS},
    {"name": "Aviva / Aviva Investors (London)",
     "category": "London private sector", "type": "workday", "profile": "finance",
     "locations": LONDON_LOCATIONS,
     "host": "aviva.wd1.myworkdayjobs.com", "tenant": "aviva", "site": "External"},
    {"name": "abrdn (London/Edinburgh)",
     "category": "London private sector", "type": "workday", "profile": "finance",
     "locations": LONDON_LOCATIONS,
     "host": "abrdn.wd3.myworkdayjobs.com", "tenant": "abrdn", "site": "abrdn"},
    {"name": "Wise (London — fintech; payments data)",
     "category": "London private sector", "type": "smartrecruiters",
     "slug": "wise", "profile": "finance", "locations": LONDON_LOCATIONS},
    {"name": "Monzo (London — credit risk & economics)",
     "category": "London private sector", "type": "greenhouse",
     "slug": "monzo", "profile": "finance", "locations": LONDON_LOCATIONS},

    # ---- bookmarks: no usable API, opened manually -------------------------
    # Every URL below returned HTTP 200 when checked, EXCEPT the three marked
    # (403) -- those block scripted requests but open normally in a browser.
    # Firms deliberately left out because no working careers URL could be
    # found: Fulcrum, Fathom, Exante Data, Insight Investment, Eisler,
    # Balyasny. Add them if you find a live link.
    {"name": "Oxford Economics (macro forecasting)", "category": "London private sector",
     "type": "link", "url": "https://careers.oxfordeconomics.com/"},
    {"name": "TS Lombard / GlobalData (macro research)", "category": "London private sector",
     "type": "link", "url": "https://careers.globaldata.com/"},
    {"name": "Frontier Economics", "category": "London private sector",
     "type": "link", "url": "https://www.frontier-economics.com/uk/en/careers/"},
    {"name": "Oxera", "category": "London private sector",
     "type": "link", "url": "https://www.oxera.com/careers/"},
    {"name": "Schroders", "category": "London private sector",
     "type": "link", "url": "https://www.schroders.com/en/global/individual/careers/"},
    {"name": "M&G Investments", "category": "London private sector",
     "type": "link", "url": "https://group.mandg.com/careers"},
    {"name": "Fidelity International", "category": "London private sector",
     "type": "link", "url": "https://careers.fidelityinternational.com/"},
    {"name": "Ninety One (EM macro)", "category": "London private sector",
     "type": "link", "url": "https://ninetyone.com/en/united-kingdom/careers"},
    {"name": "Ashmore (EM debt)", "category": "London private sector",
     "type": "link", "url": "https://www.ashmoregroup.com/en-gb/careers"},
    {"name": "HSBC (Global Research)", "category": "London private sector",
     "type": "link", "url": "https://www.hsbc.com/careers"},
    {"name": "Standard Chartered (EM macro)", "category": "London private sector",
     "type": "link", "url": "https://jobs.standardchartered.com/"},
    {"name": "Nomura", "category": "London private sector",
     "type": "link", "url": "https://www.nomura.com/careers/"},
    {"name": "Barclays", "category": "London private sector",
     "type": "link", "url": "https://search.jobs.barclays/"},
    {"name": "NatWest Group (403)", "category": "London private sector",
     "type": "link", "url": "https://jobs.natwestgroup.com/"},
    {"name": "Bloomberg Economics (403)", "category": "London private sector",
     "type": "link", "url": "https://careers.bloomberg.com/"},
    {"name": "MSCI", "category": "London private sector",
     "type": "link", "url": "https://careers.msci.com/"},
    {"name": "Revolut (403)", "category": "London private sector",
     "type": "link", "url": "https://www.revolut.com/careers/"},
    {"name": "Checkout.com", "category": "London private sector",
     "type": "link", "url": "https://www.checkout.com/careers"},
    {"name": "Jain Global (multi-strat)", "category": "London private sector",
     "type": "link", "url": "https://www.jainglobal.com/careers"},
    {"name": "Tudor Investment", "category": "London private sector",
     "type": "link", "url": "https://www.tudor.com/careers/"},
    {"name": "Aspect Capital (systematic macro)", "category": "London private sector",
     "type": "link", "url": "https://www.aspectcapital.com/careers/"},
    {"name": "Andurand Capital (commodity macro)", "category": "London private sector",
     "type": "link", "url": "https://www.andurand.com/careers"},
    # --- London catch-alls: this market fills largely through these boards --
    {"name": "LinkedIn — London: economist (newest first)",
     "category": "London private sector", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=economist&location=London%2C%20England%2C%20United%20Kingdom&sortBy=DD"},
    {"name": "LinkedIn — London: macro strategist / research",
     "category": "London private sector", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=macro%20strategist&location=London%2C%20England%2C%20United%20Kingdom&sortBy=DD"},
    {"name": "eFinancialCareers — London economist/strategist",
     "category": "London private sector", "type": "link",
     "url": "https://www.efinancialcareers.co.uk/jobs-UK-London-Economist"},

    # =======================================================================
    #  GLOBAL MACRO HEDGE FUNDS
    #  The discretionary / systematic macro shops where a central-bank-trained
    #  macro economist who can code is a genuine fit (rates, FX, inflation).
    #  No location filter: these seats are scarce, so surface all of them
    #  (London / Geneva / Zug / NY) rather than risk filtering one out.
    #  Profile "finance" keeps strategist / quant-researcher / macro-research
    #  titles. Most pure-macro funds run NO public API (Rokos, Caxton, Element,
    #  Capula, Eisler, Qube, Brevan Howard) -> bookmarks. Three multi-strats
    #  with macro/quant desks DO expose one and are scraped.
    # =======================================================================
    # ---- scraped automatically (verified working) --------------------------
    {"name": "Schonfeld (discretionary macro + quant)",
     "category": "Global macro hedge funds", "type": "greenhouse",
     "slug": "schonfeld", "profile": "finance"},
    {"name": "Squarepoint Capital (quant; posts Geneva/Zug roles)",
     "category": "Global macro hedge funds", "type": "greenhouse",
     "slug": "squarepointcapital", "profile": "finance"},
    {"name": "ExodusPoint (macro multi-strategy)",
     "category": "Global macro hedge funds", "type": "greenhouse",
     "slug": "exoduspoint", "profile": "finance"},

    # ---- pure macro funds (bookmarks — no public API) ----------------------
    {"name": "Brevan Howard (Geneva/London — global macro)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.brevanhoward.com/careers/"},
    {"name": "Rokos Capital Management (London — global macro)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.rokoscapital.com/careers"},
    {"name": "Caxton Associates (London — global macro)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.caxton.com/careers"},
    {"name": "Element Capital (macro)", "category": "Global macro hedge funds",
     "type": "link", "url": "https://www.elementcapital.com/"},
    {"name": "Capula Investment Management (macro/fixed income)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://capula.com/"},
    {"name": "Eisler Capital (macro multi-strategy)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.eisler.com/"},
    {"name": "Qube Research & Technologies (systematic)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.qube-rt.com/careers"},
    {"name": "Kirkoswald Capital (macro)", "category": "Global macro hedge funds",
     "type": "link", "url": "https://www.kirkoswald.com/"},

    # ---- aggregator searches tuned to global-macro roles -------------------
    {"name": "eFinancialCareers — 'global macro' roles",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.efinancialcareers.com/jobs?q=global%20macro"},
    {"name": "LinkedIn — 'macro strategist' (Europe, newest first)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=macro%20strategist&location=European%20Union&sortBy=DD"},
    {"name": "LinkedIn — 'quantitative researcher macro' (newest first)",
     "category": "Global macro hedge funds", "type": "link",
     "url": "https://www.linkedin.com/jobs/search/?keywords=quantitative%20researcher%20macro&sortBy=DD"},

    # ===================== International institutions ========================
    {"name": "IMF", "category": "International institutions", "type": "workday",
     "host": "imf.wd5.myworkdayjobs.com", "tenant": "imf", "site": "IMF"},
    {"name": "OECD", "category": "International institutions",
     "type": "smartrecruiters", "slug": "OECD"},

    # ===================== Central banks (clean APIs) =======================
    {"name": "Federal Reserve System (12 banks)", "category": "Central banks",
     "type": "workday", "host": "rb.wd5.myworkdayjobs.com",
     "tenant": "rb", "site": "FRS"},
    {"name": "Reserve Bank of Australia", "category": "Central banks",
     "type": "workday", "host": "rba.wd105.myworkdayjobs.com",
     "tenant": "rba", "site": "RBA_Careers"},

    # ===================== Rating agencies ==================================
    {"name": "S&P Global", "category": "Rating agencies", "type": "workday",
     "profile": "finance", "host": "spgi.wd5.myworkdayjobs.com",
     "tenant": "spgi", "site": "SPGI_Careers"},

    # ===================== Economic consultancies ===========================
    {"name": "Charles River Associates", "category": "Economic consultancies",
     "type": "greenhouse", "slug": "charlesriverassociates", "profile": "consultancy"},
    {"name": "Brattle Group", "category": "Economic consultancies",
     "type": "greenhouse", "slug": "thebrattlegroup", "profile": "consultancy"},
    {"name": "Keystone Strategy", "category": "Economic consultancies",
     "type": "greenhouse", "slug": "keystonestrategy", "profile": "consultancy"},

    # ===================== Buy-side / trading (finance profile) =============
    {"name": "AQR Capital", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "aqr", "profile": "finance"},
    {"name": "Point72", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "point72", "profile": "finance"},
    {"name": "Man Group", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "mangroup", "profile": "finance"},
    {"name": "Marshall Wace", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "marshallwace", "profile": "finance"},
    {"name": "Jane Street", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "janestreet", "profile": "finance"},
    {"name": "DRW", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "drweng", "profile": "finance"},
    {"name": "IMC Trading", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "imc", "profile": "finance"},
    {"name": "Jump Trading", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "jumptrading", "profile": "finance"},
    {"name": "Virtu Financial", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "virtu", "profile": "finance"},
    {"name": "Flow Traders", "category": "Buy-side / trading",
     "type": "greenhouse", "slug": "flowtraders", "profile": "finance"},

    # ===================== Private sector / tech (econ teams) ================
    {"name": "Airbnb",    "category": "Private sector / tech", "type": "greenhouse", "slug": "airbnb"},
    {"name": "Lyft",      "category": "Private sector / tech", "type": "greenhouse", "slug": "lyft"},
    {"name": "Instacart", "category": "Private sector / tech", "type": "greenhouse", "slug": "instacart"},
    {"name": "Pinterest", "category": "Private sector / tech", "type": "greenhouse", "slug": "pinterest"},
    {"name": "Stripe",    "category": "Private sector / tech", "type": "greenhouse", "slug": "stripe"},
    {"name": "Block",     "category": "Private sector / tech", "type": "greenhouse", "slug": "block"},
    {"name": "Roblox",    "category": "Private sector / tech", "type": "greenhouse", "slug": "roblox"},
    {"name": "Spotify",   "category": "Private sector / tech", "type": "lever", "slug": "spotify"},

    # =======================================================================
    #  BOOKMARKS — no open/permitted API, so opened manually. Grouped by the
    #  same categories on the dashboard.
    # =======================================================================
    # --- Aggregators (carry hundreds of employers each) ---------------------
    {"name": "AEA JOE — Job Openings for Economists (THE catch-all)",
     "category": "Aggregators (catch-all)", "type": "link",
     "url": "https://www.aeaweb.org/joe/listings"},
    {"name": "eFinancialCareers (buy/sell-side)", "category": "Aggregators (catch-all)",
     "type": "link", "url": "https://www.efinancialcareers.com/jobs-Economist"},
    {"name": "EconJobMarket", "category": "Aggregators (catch-all)",
     "type": "link", "url": "https://econjobmarket.org/positions"},
    {"name": "INOMICS economist jobs", "category": "Aggregators (catch-all)",
     "type": "link", "url": "https://inomics.com/jobs"},
    {"name": "Fed Econ Jobs (all Fed economist roles)",
     "category": "Aggregators (catch-all)", "type": "link",
     "url": "https://www.fedeconjobs.org/"},
    {"name": "LinkedIn: economist, senior level", "category": "Aggregators (catch-all)",
     "type": "link", "url": "https://www.linkedin.com/jobs/search/?keywords=economist&f_E=4&sortBy=DD"},

    # --- Central banks ------------------------------------------------------
    {"name": "ECB", "category": "Central banks", "type": "link",
     "url": "https://talent.ecb.europa.eu/careers"},
    {"name": "Bank of England", "category": "Central banks", "type": "link",
     "url": "https://www.bankofengland.co.uk/careers/current-vacancies"},
    {"name": "Bank of Canada", "category": "Central banks", "type": "link",
     "url": "https://www.bankofcanada.ca/careers/find-job/"},
    {"name": "BIS", "category": "Central banks", "type": "link",
     "url": "https://www.bis.org/careers/vacancies.htm"},
    {"name": "Federal Reserve Board of Governors", "category": "Central banks",
     "type": "link",
     "url": "https://frbog.taleo.net/careersection/frs_external_career_section/jobsearch.ftl"},
    # --- European central banks (no open API — direct careers pages) --------
    {"name": "Deutsche Bundesbank", "category": "Central banks", "type": "link",
     "url": "https://www.bundesbank.de/en/bundesbank/career"},
    {"name": "Banque de France", "category": "Central banks", "type": "link",
     "url": "https://www.banque-france.fr/en/banque-de-france/careers"},
    {"name": "Banca d'Italia", "category": "Central banks", "type": "link",
     "url": "https://www.bancaditalia.it/chi-siamo/lavora-con-noi/index.html?com.dotmarketing.htmlpage.language=1"},
    {"name": "Banco de España", "category": "Central banks", "type": "link",
     "url": "https://www.bde.es/wbe/en/sobre-banco/trabaja-nosotros/"},
    {"name": "De Nederlandsche Bank", "category": "Central banks", "type": "link",
     "url": "https://www.dnb.nl/en/careers/"},
    {"name": "Sveriges Riksbank", "category": "Central banks", "type": "link",
     "url": "https://www.riksbank.se/en-gb/about-the-riksbank/work-at-the-riksbank/vacancies/"},
    {"name": "Norges Bank", "category": "Central banks", "type": "link",
     "url": "https://www.norges-bank.no/en/topics/about/Vacancies/"},
    {"name": "Swiss National Bank (SNB)", "category": "Central banks", "type": "link",
     "url": "https://www.snb.ch/en/the-snb/career"},
    {"name": "Bank of Finland", "category": "Central banks", "type": "link",
     "url": "https://www.suomenpankki.fi/en/bank-of-finland/open-positions/"},
    {"name": "Central Bank of Ireland", "category": "Central banks", "type": "link",
     "url": "https://www.centralbank.ie/careers/search-careers"},
    {"name": "National Bank of Belgium", "category": "Central banks", "type": "link",
     "url": "https://www.nbb.be/en/jobs"},
    {"name": "Banco de Portugal", "category": "Central banks", "type": "link",
     "url": "https://www.bportugal.pt/en/page/recruitment"},
    {"name": "Oesterreichische Nationalbank (OeNB)", "category": "Central banks",
     "type": "link", "url": "https://www.oenb.at/en/About-Us/Career.html"},
    {"name": "Bank of Greece", "category": "Central banks", "type": "link",
     "url": "https://www.bankofgreece.gr/en/the-bank/job-opportunities"},
    {"name": "Narodowy Bank Polski (NBP)", "category": "Central banks", "type": "link",
     "url": "https://nbp.pl/en/about-us/careers/"},
    {"name": "Czech National Bank (CNB)", "category": "Central banks", "type": "link",
     "url": "https://www.cnb.cz/en/about_cnb/career/"},
    {"name": "Magyar Nemzeti Bank (MNB)", "category": "Central banks", "type": "link",
     "url": "https://www.mnb.hu/en/careers"},
    {"name": "INOMICS: central bank economist jobs (live listings)",
     "category": "Central banks", "type": "link",
     "url": "https://inomics.com/jobs?keywords=central%20bank"},

    # --- Rating agencies ----------------------------------------------------
    {"name": "Moody's", "category": "Rating agencies", "type": "link",
     "url": "https://careers.moodys.com/jobs"},
    {"name": "Fitch Ratings", "category": "Rating agencies", "type": "link",
     "url": "https://www.fitch.group/careers"},
    {"name": "Morningstar / DBRS", "category": "Rating agencies", "type": "link",
     "url": "https://careers.morningstar.com/us/en/search-results"},

    # --- Buy-side / asset managers ------------------------------------------
    {"name": "BlackRock", "category": "Buy-side / trading", "type": "link",
     "url": "https://careers.blackrock.com/search-jobs/"},
    {"name": "PIMCO", "category": "Buy-side / trading", "type": "link",
     "url": "https://www.pimco.com/en-us/our-firm/careers/job-search"},
    {"name": "Vanguard", "category": "Buy-side / trading", "type": "link",
     "url": "https://www.vanguardjobs.com/job-search-results/"},
    {"name": "Fidelity", "category": "Buy-side / trading", "type": "link",
     "url": "https://jobs.fidelity.com/search-jobs"},
    {"name": "Citadel", "category": "Buy-side / trading", "type": "link",
     "url": "https://www.citadel.com/careers/open-opportunities/"},
    {"name": "Two Sigma", "category": "Buy-side / trading", "type": "link",
     "url": "https://careers.twosigma.com/careers/OpenRoles"},
    {"name": "Bridgewater Associates", "category": "Buy-side / trading", "type": "link",
     "url": "https://www.bridgewater.com/working-at-bridgewater/career-openings"},
    {"name": "Millennium", "category": "Buy-side / trading", "type": "link",
     "url": "https://careers.mlp.com/job-search"},
    {"name": "Norges Bank Investment Management (oil fund)",
     "category": "Buy-side / trading", "type": "link",
     "url": "https://www.nbim.no/en/organisation/careers/available-positions/"},

    # --- Sell-side / banks --------------------------------------------------
    {"name": "Goldman Sachs", "category": "Sell-side / banks", "type": "link",
     "url": "https://www.goldmansachs.com/careers/our-firm/professionals/"},
    {"name": "J.P. Morgan", "category": "Sell-side / banks", "type": "link",
     "url": "https://careers.jpmorgan.com/global/en/students/programs?search=economist"},
    {"name": "Morgan Stanley", "category": "Sell-side / banks", "type": "link",
     "url": "https://www.morganstanley.com/careers/career-opportunities-search"},
    {"name": "Citi", "category": "Sell-side / banks", "type": "link",
     "url": "https://jobs.citi.com/search-jobs/economist"},
    {"name": "Barclays", "category": "Sell-side / banks", "type": "link",
     "url": "https://search.jobs.barclays/search-jobs/economist"},
    {"name": "UBS", "category": "Sell-side / banks", "type": "link",
     "url": "https://jobs.ubs.com/search"},
    {"name": "Deutsche Bank", "category": "Sell-side / banks", "type": "link",
     "url": "https://careers.db.com/professionals/search-roles/"},

    # --- Economic consultancies (manual) ------------------------------------
    {"name": "NERA Economic Consulting", "category": "Economic consultancies",
     "type": "link", "url": "https://www.nera.com/careers/find-a-role.html"},
    {"name": "Analysis Group", "category": "Economic consultancies",
     "type": "link", "url": "https://www.analysisgroup.com/careers/open-positions/"},
    {"name": "Cornerstone Research", "category": "Economic consultancies",
     "type": "link", "url": "https://www.cornerstone.com/careers/open-positions/"},
    {"name": "Compass Lexecon", "category": "Economic consultancies",
     "type": "link", "url": "https://www.compasslexecon.com/careers/open-positions/"},

    # --- Private sector -----------------------------------------------------
    {"name": "Amazon Economists", "category": "Private sector / tech",
     "type": "link", "url": "https://www.amazon.jobs/en/teams/economics"},
]

# -----------------------------------------------------------------------------
# 3. EMAIL  (optional — leave ENABLED=False for HTML dashboard only)
# -----------------------------------------------------------------------------
EMAIL = {
    "ENABLED": True,
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "FROM": "giovanni.borraccia7@gmail.com",
    # TO can be ONE address or several separated by commas (to share the digest):
    #   "TO": "giovanni.borraccia7@gmail.com, friend@example.com",
    "TO": "giovanni.borraccia7@gmail.com",
    # The password is NOT stored here anymore. In the cloud it comes from the
    # GitHub secret JOBRADAR_APP_PW; to test locally, run:
    #   JOBRADAR_APP_PW=yourapppassword python3 job_radar.py
    "APP_PASSWORD": "",
    "ONLY_WHEN_NEW": False,   # False = email daily even if nothing new, so the
                              # recipient always gets the full current dashboard
    "ATTACH_DASHBOARD": True, # attach the whole jobs.html (full listing) to the email
}
