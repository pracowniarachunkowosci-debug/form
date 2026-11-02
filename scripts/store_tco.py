"""Reproducible Issue #6 model; stdlib only, no network or private repository access.

python scripts/store_tco.py           # writes tables, report section and JSON results
python scripts/store_tco.py --check   # verifies math and committed output consistency
"""
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/store-tco'
M = json.loads((OUT/'assumptions.json').read_text(encoding='utf-8'))
CENT = D('0.01')

def money(value):
    return D(value).quantize(CENT, rounding=ROUND_HALF_UP)

def fmt(value):
    return f'{money(value):,.2f}'.replace(',', ' ').replace('.', ',')

def fee(stack, method, basket):
    rate, flat = map(D, M['payment_fees'][stack][method])
    return money(D(basket)*rate+flat)

def mixed_fee(stack, basket):
    return sum(D(weight)*fee(stack, method, basket) for method,weight in M['payment_mix'].items())

def fixed(stack, fx=None):
    p = M[stack]
    hosting = ((D(p['vercel_usd_monthly'])+D(p['neon_usd_monthly_budget'])) * D(fx or M['usd_pln_planning_rate'])
               if stack=='A' else D(p['ovh_pro_renewal_net_monthly_equivalent']))
    return hosting + D(p['email_monthly_base']) + D(p['offsite_backup_monthly_budget'])

def scenario(stack, n, basket, months, level='reference', rate=None):
    p=M[stack]; r=D(M['hourly_rate_assumption'] if rate is None else rate)
    payments=mixed_fee(stack,basket)*n*months
    tech=fixed(stack)*months+payments+D(p['activation_budget'])
    build=D(p[f'implementation_hours_{level}'])*r
    maintenance=D(p[f'maintenance_hours_{level}'])*r*months
    return {'stack':stack,'orders_monthly':n,'basket':basket,'months':months,
            'payments':payments,'fixed':fixed(stack)*months,'activation':D(p['activation_budget']),
            'technology':tech,'build':build,'maintenance':maintenance,'tco':tech+build+maintenance}

def review_annex():
    """Controlled one-variable and combined sensitivities; baseline stays unchanged."""
    a=M['review_annex']; fx=D(M['usd_pln_planning_rate'])
    assert a['confirmed_existing_vercel_pro'] is False  # No evidence for a Pro discount.
    low_neon_delta=(D(a['neon_low_usage_usd_monthly_budget'])-D(M['A']['neon_usd_monthly_budget']))*fx
    extra=D(a['direct_p24_extra_implementation_hours_reference'])
    variants=[
        ('A_base','A: Stripe, Neon 20 USD','A','A',D(0),D(0)),
        ('B_base','B: P24, OVH baza','B','B',D(0),D(0)),
        ('A_P24','A: bezpośrednie P24, Neon 20 USD','A','B',D(0),extra),
        ('A_low_neon','A: Stripe, Neon 5 USD','A','A',low_neon_delta,D(0)),
        ('A_P24_low_neon','A: bezpośrednie P24, Neon 5 USD','A','B',low_neon_delta,extra),
    ]
    for budget in a['alternative_b_hosting_net_monthly_budgets']:
        delta=D(budget)-D(M['B']['ovh_pro_renewal_net_monthly_equivalent'])
        variants.append((f'B_host_{int(D(budget))}',f'B: hosting {fmt(budget)} zł/mies. (budżet)','B','B',delta,D(0)))
    rows=[]
    lines=['| Wariant; 100 zam./mies. × 78 zł | Technologia 12 mies. | Technologia 36 mies. | Z wyceną pracy 12 mies. | Z wyceną pracy 36 mies. |',
           '| --- | ---: | ---: | ---: | ---: |']
    for key,label,stack,gateway,delta,extra_hours in variants:
        pair=[]
        for months in M['horizons_months']:
            row=scenario(stack,a['orders_monthly'],a['charged_basket_pln'],months)
            row.update(variant=key,payment_fee_schedule=gateway)
            row['fixed']+=delta*months
            row['activation']=D(M['B']['activation_budget']) if gateway=='B' else D(0)
            row['payments']=mixed_fee(gateway,a['charged_basket_pln'])*a['orders_monthly']*months
            row['extra_implementation_hours']=extra_hours
            row['build']+=extra_hours*D(M['hourly_rate_assumption'])
            row['technology_before_activation']=row['fixed']+row['payments']
            row['technology']=row['technology_before_activation']+row['activation']
            row['tco']=row['technology']+row['build']+row['maintenance']
            assert row['tco']==sum(row[k] for k in ('fixed','activation','payments','build','maintenance'))
            rows.append(row);pair.append(row)
        lines.append('| '+label+' | '+' | '.join(fmt(r[k]) for k in ('technology','tco') for r in pair)+' |')
    by_key={(r['variant'],r['months']):r for r in rows}
    assert by_key['A_P24',12]['technology_before_activation']==D('3612.00')
    assert by_key['A_P24',12]['technology']==D('3671.00')
    assert by_key['B_base',12]['technology']==D('2262.08')
    for months in M['horizons_months']:
        for stack in ('A','B'):
            ref=scenario(stack,100,78,months)
            assert all(by_key[f'{stack}_base',months][k]==v for k,v in ref.items())
        assert by_key['A_base',months]['technology']-by_key['A_low_neon',months]['technology']==D(60)*months
        assert by_key['A_P24_low_neon',months]['technology']==by_key['B_host_100',months]['technology']
    for key,*_ in variants:
        first=by_key[key,12];last=by_key[key,36]
        assert last['tco']==3*first['tco']-2*(first['activation']+first['build'])
    return '\n'.join(lines),rows

def generate():
    assert sum(map(D,M['payment_mix'].values()))==1
    assert fee('A','blik',78)==D('2.25')
    assert fee('B','blik',78)==D('1.31')
    assert mixed_fee('A',78)==D('2.257')
    assert mixed_fee('B',78)==D('1.31')
    assert fixed('A')==170 and fixed('B')==D('52.59')
    for n in M['order_volumes_monthly']:
        assert all(n*D(w)==int(n*D(w)) for w in M['payment_mix'].values())
    rows=[]
    lines=['# Obliczenia TCO — wygenerowane z assumptions.json','',
           'Data źródeł: 2026-11-02. Wszystkie wyniki w PLN. Założenia, VAT, wyłączenia i źródła: [raport](../STORE_TCO_NEXT_VS_WOO.md).', '',
           '## Prowizja od jednej opłaconej transakcji','',
           '| Koszyk brutto | A: BLIK | A: karta EOG standard | A: przelew P24 przez Stripe | B: BLIK/karta 3DS/przelew | A: średnia miksu* | B: średnia miksu |',
           '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s in M['charged_baskets_pln']:
        lines.append('| '+' | '.join([fmt(s),fmt(fee('A','blik',s)),fmt(fee('A','eea_standard_card',s)),fmt(fee('A','online_transfer',s)),fmt(fee('B','blik',s)),str(mixed_fee('A',s)).replace('.',','),str(mixed_fee('B',s)).replace('.',',')])+' |')
    lines+=['','*Średnia ważona 70% BLIK / 20% standardowych kart EOG / 10% przelewów; nie zaokrąglamy średniej przed mnożeniem przez liczbę transakcji. Każda pojedyncza prowizja zaokrąglana do grosza HALF_UP jako jawne założenie modelu.','']
    for months in M['horizons_months']:
        lines += [f'## {months} miesięcy','',
                  '| Zam./mies. | Koszyk brutto | A: technologia + prowizje | B: technologia + prowizje | A: z pracą i utrzymaniem | B: z pracą i utrzymaniem |',
                  '| ---: | ---: | ---: | ---: | ---: | ---: |']
        for n in M['order_volumes_monthly']:
            for s in M['charged_baskets_pln']:
                a=scenario('A',n,s,months);b=scenario('B',n,s,months)
                rows.extend([a,b])
                lines.append('| '+' | '.join([str(n),fmt(s),fmt(a['technology']),fmt(b['technology']),fmt(a['tco']),fmt(b['tco'])])+' |')
        lines.append('')
    lines+=['## Zakres nakładu pracy — koszyk 78 zł, stawka nadal 150 zł/h','',
            '| Zam./mies. | Miesiące | A: niski–wysoki | B: niski–wysoki |',
            '| ---: | ---: | ---: | ---: |']
    for n in M['order_volumes_monthly']:
        for months in M['horizons_months']:
            bounds=[f"{fmt(scenario(v,n,78,months,'low')['tco'])}–{fmt(scenario(v,n,78,months,'high')['tco'])}" for v in ('A','B')]
            lines.append(f'| {n} | {months} | {bounds[0]} | {bounds[1]} |')
    lines+=['','## Opcja: limitowany druk płatny od miesiąca 7','',
            'Przyrost względem odpowiedniej tabeli bazowej, bez zmiany wolumenu/prowizji; zawiera wdrożenie i dodatkowe 0,5 h utrzymania/mies. od miesiąca 7.', '',
            '| Horyzont | A: dodatkowo | B: dodatkowo |','| ---: | ---: | ---: |']
    for months in M['horizons_months']:
        active=max(0,months-M['optional_mto_start_month']+1)
        adds=[(D(M[v]['mto_hours_reference'])+D(M['optional_mto_extra_maintenance_hours_monthly'])*active)*D(M['hourly_rate_assumption']) for v in ('A','B')]
        lines.append(f'| {months} mies. | {fmt(adds[0])} | {fmt(adds[1])} |')
    lines+=['','## Wrażliwość na stawkę pracy — 100 zam./mies., koszyk 78 zł','',
            '| Stawka planistyczna | A: 12 mies. | B: 12 mies. | A: 36 mies. | B: 36 mies. |','| ---: | ---: | ---: | ---: | ---: |']
    for rate in (0,100,150,200):
        vals=[fmt(scenario(v,100,78,m,rate=str(rate))['tco']) for m in (12,36) for v in ('A','B')]
        lines.append('| '+str(rate)+' zł/h | '+' | '.join(vals)+' |')
    lines+=['','0 zł/h pokazuje własną pracę bez wyceny czasu, nie zerowy nakład pracy.','',
            '## Próg korzyści z automatyzacji w A','',
            'Hipoteza: dodatkowa oszczędność operacyjna względem B, wartość czasu 50 zł/h, odzyskanie różnicy referencyjnego TCO w 36 miesięcy; koszyk 78 zł. To wymagany próg, nie zmierzona przewaga A.', '',
            '| Zam./mies. | Różnica TCO A−B, 36 mies. | Wymagana oszczędność minut/zamówienie |',
            '| ---: | ---: | ---: |']
    for n in M['order_volumes_monthly']:
        delta=scenario('A',n,78,36)['tco']-scenario('B',n,78,36)['tco']
        minutes=delta/(36*n*D(50)/60)
        lines.append(f'| {n} | {fmt(delta)} | {fmt(minutes)} |')
    # Cross-check additive accounting and horizon relation: one build + activation only.
    for row in rows:
        assert row['tco']==row['fixed']+row['activation']+row['payments']+row['build']+row['maintenance']
    for v in ('A','B'):
        a=scenario(v,100,78,12);b=scenario(v,100,78,36)
        assert b['tco']==3*a['tco']-2*(a['build']+a['activation'])
    annex,review_rows=review_annex()
    payload=json.dumps({'model_date':M['as_of'],'scenarios':rows,'review_annex_scenarios':review_rows},ensure_ascii=False,indent=2,default=str)+'\n'
    return '\n'.join(lines)+'\n',payload,annex

if __name__=='__main__':
    md,payload,annex=generate()
    report=ROOT/'docs/STORE_TCO_NEXT_VS_WOO.md'
    current=report.read_text(encoding='utf-8')
    start='<!-- BEGIN GENERATED TCO -->'
    end='<!-- END GENERATED TCO -->'
    assert current.count(start)==current.count(end)==1
    prefix,rest=current.split(start)
    _,suffix=rest.split(end)
    embedded=md[md.index('## Prowizja'):]
    embedded='\n'.join('#'+line if line.startswith('## ') else line for line in embedded.splitlines())
    updated=prefix+start+'\n\n'+embedded+'\n\n'+end+suffix
    start='<!-- BEGIN REVIEW ANNEX TCO -->'
    end='<!-- END REVIEW ANNEX TCO -->'
    assert updated.count(start)==updated.count(end)==1
    prefix,rest=updated.split(start)
    _,suffix=rest.split(end)
    updated=prefix+start+'\n\n'+annex+'\n\n'+end+suffix
    for target,content in [(OUT/'tables.md',md),(OUT/'results.json',payload),(report,updated)]:
        if '--check' in sys.argv:
            assert target.read_text(encoding='utf-8')==content, f'Regenerate {target}'
        else:
            target.write_text(content,encoding='utf-8')
    print('PASS: 36 baseline + 16 review scenarios; fee rounding, symmetric P24 activation, low usage/hosting sensitivity, accounting identities and deterministic report/JSON outputs.')
