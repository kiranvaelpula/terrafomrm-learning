# Chargeback vs Showback Models

**Implementing financial accountability for cloud spend**

---

## 📖 Overview

**Chargeback** and **Showback** are two approaches to make teams financially accountable for their cloud spending:

- **Showback**: Show teams their costs (visibility only, no money transfer)
- **Chargeback**: Charge teams for their actual costs (financial transaction)

**Why It Matters:**
- **Behavioral change** - Teams optimize when they see/pay costs
- **Budget accountability** - Each team owns their spend
- **Fair allocation** - Costs go to those who create them
- **Executive visibility** - Clear cost centers

**Reality in 2026:**
- 68% of enterprises use showback
- 45% use chargeback for some teams
- 23% use hybrid (showback → chargeback transition)

---

## 🆚 Showback vs Chargeback

### **Showback (Informational)**

**Definition:** Report costs to teams without actual money transfer

```
Monthly Report to Mobile Team:
┌────────────────────────────────┐
│ Mobile Team Cloud Costs - June│
├────────────────────────────────┤
│ Production:        $78,000     │
│ Staging:            $8,000     │
│ Development:        $6,000     │
├────────────────────────────────┤
│ TOTAL:             $92,000     │
└────────────────────────────────┘

ℹ️ Informational only - no budget impact
```

**Characteristics:**
- ✅ Visibility without consequences
- ✅ Easy to implement (just reporting)
- ✅ Good for starting FinOps journey
- ⚠️ Less motivation to optimize
- ⚠️ No budget enforcement

**Best For:**
- Early-stage FinOps (first 3-6 months)
- Teams learning cloud costs
- Shared services teams
- R&D / innovation projects

### **Chargeback (Financial)**

**Definition:** Actually charge teams' budgets for their cloud usage

```
Monthly Invoice to Mobile Team:
┌────────────────────────────────┐
│ Mobile Team Cloud Invoice - June
├────────────────────────────────┤
│ Production:        $78,000     │
│ Staging:            $8,000     │
│ Development:        $6,000     │
├────────────────────────────────┤
│ TOTAL:             $92,000     │
│                                │
│ Budget:           $85,000      │
│ OVER BUDGET:       $7,000 ❌   │
└────────────────────────────────┘

💳 Charged to cost center CC-2045
⚠️ $7,000 over budget - optimization required
```

**Characteristics:**
- ✅ Real financial accountability
- ✅ Strong motivation to optimize
- ✅ Budget discipline
- ⚠️ Requires accurate cost allocation
- ⚠️ Finance process overhead
- ⚠️ Can slow innovation if too strict

**Best For:**
- Mature FinOps organizations
- Product/profit-center teams
- Teams with dedicated budgets
- After 6+ months of showback

---

## 🎯 Showback Implementation

### **Step 1: Cost Allocation (Foundation)**

```python
# scripts/generate_showback_report.py
import boto3
from datetime import datetime, timedelta
from collections import defaultdict
import json

ce = boto3.client('ce')

def get_costs_by_team(start_date, end_date):
    """
    Get costs grouped by Team tag
    """
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'TAG', 'Key': 'Team'},
            {'Type': 'TAG', 'Key': 'Environment'}
        ]
    )
    
    costs = defaultdict(lambda: defaultdict(float))
    
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            keys = group['Keys']
            team = keys[0].split('$')[1] if '$' in keys[0] else 'Untagged'
            env = keys[1].split('$')[1] if '$' in keys[1] else 'Untagged'
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            
            costs[team][env] += cost
    
    return costs

def generate_showback_report(year, month):
    """
    Generate monthly showback report for all teams
    """
    # Calculate date range
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
    
    costs = get_costs_by_team(start_date, end_date)
    
    print(f"\n📊 SHOWBACK REPORT - {year}-{month:02d}")
    print("=" * 80)
    
    team_totals = []
    
    for team in sorted(costs.keys()):
        team_costs = costs[team]
        total = sum(team_costs.values())
        team_totals.append((team, total))
        
        print(f"\n{team.upper()}")
        print("-" * 80)
        
        for env in ['production', 'staging', 'development', 'testing']:
            if env in team_costs:
                cost = team_costs[env]
                pct = (cost / total * 100) if total > 0 else 0
                print(f"  {env:15} ${cost:>12,.2f} ({pct:>5.1f}%)")
        
        # Handle untagged or other environments
        other_envs = set(team_costs.keys()) - {'production', 'staging', 'development', 'testing'}
        for env in other_envs:
            cost = team_costs[env]
            pct = (cost / total * 100) if total > 0 else 0
            print(f"  {env:15} ${cost:>12,.2f} ({pct:>5.1f}%)")
        
        print(f"  {'-' * 15} {'-' * 13} {'-' * 7}")
        print(f"  {'TOTAL':15} ${total:>12,.2f}")
    
    # Overall summary
    grand_total = sum(total for _, total in team_totals)
    print(f"\n{'=' * 80}")
    print(f"GRAND TOTAL: ${grand_total:,.2f}")
    print()
    
    # Top spenders
    team_totals.sort(key=lambda x: x[1], reverse=True)
    print("Top 5 Teams by Spend:")
    for rank, (team, total) in enumerate(team_totals[:5], 1):
        pct = (total / grand_total * 100) if grand_total > 0 else 0
        print(f"  {rank}. {team:20} ${total:>12,.2f} ({pct:>5.1f}%)")
    
    return costs

if __name__ == '__main__':
    # Generate report for current month
    now = datetime.now()
    generate_showback_report(now.year, now.month)
```

### **Step 2: Automated Email Reports**

```python
# scripts/email_showback_reports.py
import boto3
from datetime import datetime
import json

ses = boto3.client('ses')
ce = boto3.client('ce')

TEAM_CONTACTS = {
    'platform': ['platform-leads@company.com'],
    'mobile': ['mobile-leads@company.com'],
    'data': ['data-leads@company.com'],
    'ml': ['ml-leads@company.com']
}

def create_team_email_html(team, costs, prev_costs):
    """
    Create HTML email for team showback report
    """
    total = sum(costs.values())
    prev_total = sum(prev_costs.values())
    change_pct = ((total - prev_total) / prev_total * 100) if prev_total > 0 else 0
    trend = "📈" if change_pct > 5 else "📉" if change_pct < -5 else "➡️"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #34495e; color: white; }}
            .total-row {{ font-weight: bold; background-color: #ecf0f1; }}
            .alert {{ background-color: #e74c3c; color: white; padding: 10px; margin: 10px 0; }}
            .info {{ background-color: #3498db; color: white; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Cloud Cost Showback Report</h1>
            <p>{team.title()} Team - {datetime.now().strftime('%B %Y')}</p>
        </div>
        
        <div class="content">
            <h2>Monthly Summary</h2>
            <p>
                <strong>Total Cloud Spend:</strong> ${total:,.2f}<br>
                <strong>vs Last Month:</strong> ${prev_total:,.2f} {trend} {change_pct:+.1f}%
            </p>
            
            {"<div class='alert'>⚠️ Costs increased significantly this month</div>" if change_pct > 10 else ""}
            
            <h3>Cost Breakdown</h3>
            <table>
                <tr>
                    <th>Environment</th>
                    <th>Current Month</th>
                    <th>Last Month</th>
                    <th>Change</th>
                </tr>
    """
    
    for env in ['production', 'staging', 'development']:
        current = costs.get(env, 0)
        previous = prev_costs.get(env, 0)
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        
        html += f"""
                <tr>
                    <td>{env.title()}</td>
                    <td>${current:,.2f}</td>
                    <td>${previous:,.2f}</td>
                    <td>{change:+.1f}%</td>
                </tr>
        """
    
    html += f"""
                <tr class="total-row">
                    <td>TOTAL</td>
                    <td>${total:,.2f}</td>
                    <td>${prev_total:,.2f}</td>
                    <td>{change_pct:+.1f}%</td>
                </tr>
            </table>
            
            <div class="info">
                ℹ️ This is a showback report (informational only). No budget charges applied.
            </div>
            
            <h3>Optimization Recommendations</h3>
            <ul>
                <li>Review <a href="https://console.aws.amazon.com/cost-explorer">Cost Explorer</a> for detailed breakdown</li>
                <li>Check for unused resources in development environments</li>
                <li>Consider Reserved Instances for stable workloads</li>
                <li>Contact #finops-help for optimization assistance</li>
            </ul>
            
            <p>
                <small>
                    Questions? Contact finops@company.com<br>
                    View detailed costs: <a href="https://company-finops-dashboard.com">FinOps Dashboard</a>
                </small>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_showback_email(team, email_html):
    """
    Send showback email via SES
    """
    recipients = TEAM_CONTACTS.get(team, [])
    if not recipients:
        print(f"⚠️ No email contacts for team: {team}")
        return
    
    try:
        response = ses.send_email(
            Source='finops@company.com',
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {
                    'Data': f'Cloud Cost Report - {team.title()} Team - {datetime.now().strftime("%B %Y")}'
                },
                'Body': {
                    'Html': {'Data': email_html}
                }
            }
        )
        print(f"✅ Sent showback email to {team}: {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Failed to send email to {team}: {str(e)}")

# Usage
team = 'platform'
current_costs = {'production': 95000, 'staging': 8000, 'development': 5000}
previous_costs = {'production': 89000, 'staging': 7500, 'development': 6000}

email_html = create_team_email_html(team, current_costs, previous_costs)
send_showback_email(team, email_html)
```

