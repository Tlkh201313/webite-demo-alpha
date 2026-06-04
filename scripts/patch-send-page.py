"""One-off patch: clean up nsc-life/send.html layout."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEND = ROOT / "nsc-life" / "send.html"

CSS = """
            /* SEND page layout */
            .send-lead {
                font-size: 1.0625rem;
                line-height: 1.65;
                color: #191c1d;
            }
            .send-section {
                margin-top: 2.5rem;
                padding-top: 2rem;
                border-top: 1px solid rgba(73, 14, 103, 0.1);
            }
            .send-section:first-child {
                margin-top: 0;
                padding-top: 0;
                border-top: none;
            }
            .send-section h2 {
                font-family: "Hanken Grotesk", sans-serif;
                font-size: 1.375rem;
                font-weight: 600;
                color: #490e67;
                margin: 0 0 1rem;
                letter-spacing: -0.01em;
            }
            .send-section h3 {
                font-family: "Hanken Grotesk", sans-serif;
                font-size: 1.125rem;
                font-weight: 600;
                color: #490e67;
                margin: 0 0 0.75rem;
            }
            .send-section ul:not(.send-link-list) {
                margin: 0.75rem 0 1rem;
                padding-left: 1.25rem;
            }
            .send-section li + li {
                margin-top: 0.35rem;
            }
            .send-contact-card {
                margin: 1.5rem 0 0;
                padding: 1.25rem 1.5rem;
                background: #f3ebf6;
                border-left: 4px solid #490e67;
                border-radius: 0 0.5rem 0.5rem 0;
            }
            .send-contact-card dl {
                display: grid;
                gap: 0.875rem;
                margin: 0;
            }
            .send-contact-card dt {
                font-family: "Hanken Grotesk", sans-serif;
                font-weight: 600;
                color: #490e67;
                font-size: 0.875rem;
            }
            .send-contact-card dd {
                margin: 0.15rem 0 0;
                font-size: 0.9375rem;
            }
            .send-link-list {
                list-style: none;
                padding: 0;
                margin: 1rem 0 0;
                display: grid;
                gap: 0.5rem;
            }
            .send-link-list a {
                display: flex;
                align-items: center;
                gap: 0.625rem;
                padding: 0.75rem 1rem;
                background: #ffffff;
                border: 1px solid rgba(73, 14, 103, 0.12);
                border-radius: 0.5rem;
                text-decoration: none;
                font-weight: 600;
                color: #490e67;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
            }
            .send-link-list a:hover {
                border-color: rgba(73, 14, 103, 0.25);
                box-shadow: 0 4px 16px rgba(73, 14, 103, 0.08);
                transform: translateY(-1px);
                color: #350053;
            }
            .send-link-list a .material-symbols-outlined {
                font-size: 1.125rem;
                color: #85419d;
                flex-shrink: 0;
            }
            .send-team-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr));
                gap: 1rem;
                margin-top: 1.25rem;
            }
            @media (min-width: 640px) {
                .send-team-grid {
                    grid-template-columns: repeat(auto-fill, minmax(10.5rem, 1fr));
                    gap: 1.25rem;
                }
            }
            .send-team-card {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 1rem 0.75rem;
                background: #faf8fb;
                border: 1px solid rgba(73, 14, 103, 0.08);
                border-radius: 0.5rem;
                transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
            }
            .send-team-card:hover {
                border-color: rgba(73, 14, 103, 0.18);
                box-shadow: 0 6px 20px rgba(73, 14, 103, 0.08);
                transform: translateY(-2px);
            }
            .send-team-card__photo {
                width: 100%;
                max-width: 7.5rem;
                aspect-ratio: 3 / 4;
                object-fit: cover;
                border-radius: 0.375rem;
                margin-bottom: 0.75rem;
                box-shadow: 0 4px 14px rgba(73, 14, 103, 0.1);
                background: #e1e3e4;
            }
            .send-team-card__name {
                font-family: "Hanken Grotesk", sans-serif;
                font-size: 0.9375rem;
                font-weight: 600;
                color: #490e67;
                line-height: 1.3;
            }
            .send-team-card__role {
                font-size: 0.8125rem;
                line-height: 1.35;
                color: #4c444f;
                margin-top: 0.25rem;
            }
            .send-transition-note {
                padding: 1rem 1.25rem;
                background: rgba(44, 121, 186, 0.08);
                border-radius: 0.5rem;
                border-left: 4px solid #2c79ba;
            }
"""

TEAM = [
    ("Mrs Nicola Nevin", "SENCO", "2025/09/Nicola-Nevin-scaled.jpg"),
    ("Mrs Yasmin Burgess", "Teaching Assistant", "2024/10/Yasmin-Burgess-scaled.jpg"),
    ("Mrs Susannah Collison", "HLTA / Assistant SENCO", "2025/09/Susannah-Collison.jpg"),
    ("Mrs Paula Dopadlik", "HLTA / Assistant SENCO", "2025/09/PDopadlik-scaled.jpg"),
    ("Miss Louisa Ecclestone", "Teaching Assistant", "2025/09/Louisa-Ecclestone.jpg"),
    ("Mrs Laura Efthymiou", "Teaching Assistant", "2024/10/Laura-Demetriou.jpg"),
    ("Ms Najoua Er-rahhali", "Teaching Assistant", "2025/04/Najoua.jpeg"),
    ("Mrs Esther Fung", "Teaching Assistant", "2023/09/Esther-Fung-1-scaled.jpg"),
    ("Mr Quin O'Sullivan", "Teaching Assistant", "2024/10/Quin-OSullivan-scaled.jpg"),
    ("Mrs Lisa Veit", "Teaching Assistant", "2022/11/Lisa-Veit-scaled.jpg"),
    ("Mrs Susan Walton", "HLTA (HIVE Manager)", "2023/09/Susan-Walton-scaled.jpg"),
]

FALLBACK_JS = """
        window.nscStaffImgFallback = function (img) {
            const chain = (img.getAttribute('data-fallback-src') || '').split('|').filter(Boolean);
            if (!chain.length) return;
            img.onerror = null;
            img.src = chain.shift();
            if (chain.length) {
                img.setAttribute('data-fallback-src', chain.join('|'));
                img.onerror = function () { window.nscStaffImgFallback(img); };
            }
        };
"""


def cdn(path: str) -> str:
    return f"https://i0.wp.com/www.northstowesc.org/wp-content/uploads/{path}?resize=160,213&ssl=1"


def origin(path: str) -> str:
    return f"https://www.northstowesc.org/wp-content/uploads/{path}"


def team_card(name: str, role: str, path: str) -> str:
    src = cdn(path)
    fb = origin(path)
    return f"""<article class="send-team-card reveal-stagger-child">
<img class="send-team-card__photo" src="{src}" alt="" loading="lazy" decoding="async" width="120" height="160" data-fallback-src="{fb}" onerror="window.nscStaffImgFallback&&window.nscStaffImgFallback(this)"/>
<p class="send-team-card__name">{name}</p>
<p class="send-team-card__role">{role}</p>
</article>"""


def build_entry() -> str:
    team_html = "\n".join(team_card(n, r, p) for n, r, p in TEAM)
    return f"""<div class="entry-content learning-stagger">
<section class="send-section">
<p class="send-lead"><strong>Special Educational Needs and Disabilities (SEND)</strong> — Northstowe Secondary College is committed and passionate about ensuring ‘Achievement for All’, by setting high aspirations and providing a high quality teaching and learning environment, for all students. However, we acknowledge that some students require additional support, for part or all of their time with us, to enable them to reach their full potential.</p>
<p class="send-lead">NSC has a dedicated team who strive to provide the best provision for students with special educational needs and disabilities. For any SEND enquiries, please contact <a href="mailto:Nest@northstowe.education">Nest@northstowe.education</a>.</p>
<p class="send-lead">The following part of this website is to assist parents, carers and students in finding information about special educational needs and disabilities (SEND).</p>
<div class="send-contact-card">
<dl>
<div><dt>SENCo</dt><dd>Nicola Nevin — <a href="mailto:NNevin@northstowe.education">NNevin@northstowe.education</a></dd></div>
<div><dt>SEND Academy Councillor</dt><dd>Emma Hartshorne — <a href="mailto:EHartshorne@Martinbacon.academy">EHartshorne@Martinbacon.academy</a></dd></div>
</dl>
</div>
</section>

<section class="send-section">
<h2>Local Offer</h2>
<p>The SEN and Disability Local Offer describes what help, support and services are available for children and young people with Special Educational Needs and Disabilities (SEND) and their families in Cambridgeshire.</p>
<p>It will:</p>
<ul>
<li>Include information about education, social care and health services, as well as services provided by voluntary and community groups</li>
<li>Provide information about services for children and young people with Education, Health and Care Plans, as well as those without</li>
<li>Set out clearly the criteria for getting support</li>
<li>Be published on the internet, as well as be available in other formats on request</li>
</ul>
<p><a href="https://www.cambridgeshire.gov.uk/residents/children-and-families/local-offer/" target="_blank" rel="noreferrer noopener">Cambridgeshire Local Offer</a> provides everything you need to know about Education, Social Care, Health, information on parent support and activities for Children and young people (0–25 with a Special Educational Need and/or Disability) and their families.</p>
</section>

<section class="send-section">
<h2>Educational, Health Care Plans (EHCP)</h2>
<p>Also known as an EHC Plan, the plans are legal documents that local authorities have to follow and include information and support about the child/young person’s special education needs, as well as health and social care where relevant. In order to receive a plan a child/young person does not need to have all 3 strands of Education, Health and Social Care needs. As long as there is an educational need they can receive a plan and if the child has any health and/or social care needs this will be incorporated as well.</p>
<p>The plans can start from a child’s birth and continue into further education and training (including apprenticeship, traineeships and supported internships), and for some young people until they are 25 years old. The child/young person will own the plan, but there will also be a number of support agencies working with families as well. A child/young person’s viewpoint will be sought wherever possible whatever their circumstances and ability.</p>
<p>The assessment process for an EHC plan will take into account all provision that is currently put into place and the information will be gathered from all involvements for the child/young person.</p>
<p>For more information about EHC Plans, please visit our <a href="https://www.cambridgeshire.gov.uk/residents/children-and-families/local-offer/education-health-and-care-plan-ehcp/" target="_blank" rel="noreferrer noopener">Local Offer</a>.</p>
</section>

<section class="send-section">
<h2>Northstowe Secondary College SEND Information Report</h2>
<p>As per the SEND Code of Practice (Section 6.79), academy’s must publish information about their arrangements for identifying, assessing and making provision available for pupils with SEND. Northstowe Secondary College's information report can be found below:</p>
<ul class="send-link-list">
<li><a href="https://www.northstowesc.org/wp-content/uploads/2024/10/NSC_SEND-Information-Report_2024_2025.pdf" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">description</span>NSC SEND Information Report 2024–25</a></li>
</ul>
</section>

<section class="send-section">
<h2>Ordinarily Available Provision</h2>
<p>At Northstowe Secondary College we endeavour to meet the needs of any young person with special educational needs and/or disability. As part of this we have a universal offer to students and this is outlined in our Ordinarily Available Provision document below.</p>
<ul class="send-link-list">
<li><a href="https://www.northstowesc.org/wp-content/uploads/2022/11/Meridian-Trust-OAP-NSC.pdf" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">description</span>NSC Ordinarily Available Provision</a></li>
<li><a href="https://www.cambslearntogether.co.uk/cambridgeshire-send/cambridgeshire-send-oap-toolkits/send-oap-toolkit" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>SEND OAP Toolkit — Learn Together</a></li>
</ul>
<p>You can also use the SEND OAP Toolkit link above, which will take you to the Local Authority’s website designed to support and inform parents.</p>
</section>

<section class="send-section">
<h2>SEND Information Leaflets</h2>
<p>Some useful leaflets to help you support your child’s needs. If you require any further information please do not hesitate to contact us at the college:</p>
<ul class="send-link-list">
<li><a href="https://ccc-live.storage.googleapis.com/upload/www.cambridgeshire.gov.uk/residents/libraries-leisure-&amp;-culture/DYSLEXIA_GUIDANCE_May_2016_3.pdf?inline=true" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">description</span>Cambridgeshire Dyslexia Guidance</a></li>
<li><a href="http://www.cambscommunityservices.nhs.uk/docs/default-source/leaflets---children%27s-ot-service---april-2015/0045---children%27s-ot-service.pdf?sfvrsn=2" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">description</span>Children's Occupational Therapy</a></li>
<li><a href="http://www.cambscommunityservices.nhs.uk/what-we-do/children-young-people-health-services-cambridgeshire/specialist-services/childrens-speech-and-language-therapy/my-child" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>Speech, Language and Communication Needs</a></li>
</ul>
</section>

<section class="send-section">
<h2>SEND Information Websites</h2>
<p>Some useful websites to help you support your child’s needs. If you require any further information please do not hesitate to contact us at the college:</p>
<ul class="send-link-list">
<li><a href="https://send.cambridgeshire.gov.uk/kb5/cambridgeshire/directory/site.page?id=MR9QIFVa_9Q" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>SENDIASS</a></li>
<li><a href="https://www.pinpoint-cambs.org.uk/" target="_blank" rel="noreferrer noopener"><span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>Pinpoint</a></li>
</ul>
</section>

<section class="send-section">
<h2>SEND Policies and Procedures</h2>
<p>All of our policies, including our SEND policies, can be found on our <a href="../about/policies-statutory-information.html">Policies and Statutory Information</a> page.</p>
</section>

<section class="send-section">
<h2>SEND Transition</h2>
<div class="send-transition-note">
<h3>Welcome new Year 7s!</h3>
<p style="margin:0">This page has been created to help make your transition to secondary school a little easier.</p>
</div>
</section>

<section class="send-section" id="send-team">
<h2>Meet the Team</h2>
<div class="send-team-grid reveal-stagger-group">
{team_html}
</div>
</section>

<section class="send-section">
<h2>Where to find us</h2>
<p>We are based in the NEST (<strong>N</strong>orthstowe <strong>E</strong>ducation <strong>S</strong>upport <strong>T</strong>eam). This is located on the top floor next to the Science department. If you are unable to find us then drop into one of the house offices and one of our very friendly Student Support Assistants will show you where to go.</p>
</section>
</div>"""


def main() -> None:
    page = SEND.read_text(encoding="utf-8")

    if "/* SEND page layout */" not in page:
        page = page.replace(
            "            /* Nav: mobile accordion (northstowesc.org) + desktop flyouts at 48em */",
            CSS + "\n            /* Nav: mobile accordion (northstowesc.org) + desktop flyouts at 48em */",
            1,
        )

    page, n = re.subn(
        r'<div class="entry-content learning-stagger">.*?</div>\s*(?=</article>)',
        build_entry() + "\n",
        page,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"entry-content replace failed: {n}")

    if "window.nscStaffImgFallback" not in page:
        page = page.replace("<script>\n", "<script>\n" + FALLBACK_JS, 1)

    SEND.write_text(page, encoding="utf-8")
    print(f"Updated {SEND.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
