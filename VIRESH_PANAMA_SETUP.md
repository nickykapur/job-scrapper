# Viresh Rajani - Panama Job Scraping Setup

## Account Configuration

**Username:** `viresh_rajani2`
**Email:** vireshrajani@gmail.com
**Location:** Panama (Panama City)
**Status:** Active ✅

## Job Preferences Configured

Based on Viresh's CV (Industrial Engineer with 7+ years experience):

### Job Types
- **Sales** (Key Account Manager, Commercial Coordinator)
- **HR** (Human Resources, Talent Acquisition)
- **Finance** (Business Intelligence, Commercial Analytics)

### Experience Levels
- Mid-level
- Senior-level

### Keywords (English & Spanish)
- customer service / servicio al cliente
- commercial / comercial
- business intelligence / inteligencia de negocios
- key account / cuentas clave
- sales coordinator / coordinador de ventas
- HR / RRHH / recursos humanos
- data analytics / analítica de datos
- power bi
- industrial engineer / ingeniero industrial
- supply chain / cadena de suministro
- logistics / logística
- operations / operaciones

## Scraping Schedule

### Automated Daily Scraping
The system automatically scrapes Panama jobs **7 times per day** at:
- 9:00 AM (Dublin time)
- 11:00 AM
- 1:00 PM
- 3:00 PM
- 4:00 PM
- 6:00 PM
- 8:00 PM

Each run scrapes jobs posted in the **last 24 hours**.

### Search Terms (46 total - Spanish & English)

#### Sales & Key Account Management
**English:** key account manager, sales coordinator, commercial coordinator, account executive, business development
**Spanish:** gerente de cuentas clave, coordinador de ventas, coordinador comercial, ejecutivo de cuentas, desarrollo de negocios

#### Customer Service
**English:** customer service coordinator, customer service manager, client relations
**Spanish:** coordinador servicio al cliente, gerente servicio al cliente, relaciones con clientes

#### Human Resources
**English:** human resources coordinator, HR manager, talent acquisition, recruitment specialist
**Spanish:** coordinador recursos humanos, gerente RRHH, adquisición de talento, reclutamiento

#### Business Intelligence & Analytics
**English:** business intelligence analyst, commercial analyst, data analyst, business analyst
**Spanish:** analista de inteligencia de negocios, analista comercial, analista de datos, analista de negocios

#### Operations & Supply Chain
**English:** operations coordinator, supply chain coordinator, logistics coordinator, industrial engineer
**Spanish:** coordinador de operaciones, coordinador cadena de suministro, coordinador logística, ingeniero industrial

## Historical Scrape (Initial Backfill)

**Status:** Running
**Time Range:** Past 30 days (covers last 2 weeks)
**Search Terms:** All 46 terms (English + Spanish)
**Purpose:** Populate Viresh's account with existing job postings

## Language Support

The scraper handles **both Spanish and English** job postings:
- LinkedIn automatically shows jobs in both languages for Panama
- Search terms are provided in both languages to maximize coverage
- Job titles and descriptions can be in either language

## How It Works

1. **User Logs In:** Viresh logs in at https://web-production-110bb.up.railway.app
2. **Personalized Jobs:** Only sees jobs matching his preferences (Panama, Sales/HR/Finance)
3. **Auto-Updated:** New jobs appear automatically 7x daily
4. **Bilingual:** Jobs in both English and Spanish are included

## CV Match

Jobs scraped align with Viresh's experience:

| CV Experience | Job Types Scraped |
|--------------|------------------|
| L'Oréal Customer Service Coordinator | Customer Service roles |
| L'Oréal HR Intern | Human Resources roles |
| L'Oréal Commercial Coordinator & BI | Business Intelligence, Commercial Analyst |
| Kellanova Key Account Supervisor | Key Account Manager, Sales |
| Industrial Engineering Degree | Operations, Supply Chain, Logistics |

## Next Steps

1. ✅ User configuration complete
2. 🔄 Historical scrape running (past 2 weeks)
3. ✅ Daily automated scraping active (7x/day)
4. 📧 Viresh can login and start browsing Panama jobs immediately

## Monitoring

- **View Jobs:** https://web-production-110bb.up.railway.app
- **Admin Panel:** https://web-production-110bb.up.railway.app (software_admin account)
- **User Activity:** Check "User Analytics" in admin panel
- **Country Stats:** Check "Country Analytics" > Panama

---

**Setup Completed:** January 2026
**Automated by:** Claude Code
