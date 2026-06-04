"""Replace scraped WP accordions on student-leadership.html with structured markup."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "learning" / "enrichment" / "student-leadership.html"

NEW_CONTENT = r'''<div class="entry-content learning-stagger">
<p class="leadership-lead">Student leadership gives every young person a voice in shaping school life — through formal roles, events, and consultations.</p>

<section class="leadership-aims" aria-labelledby="leadership-aims-title">
<h2 class="leadership-aims__title" id="leadership-aims-title">Our aim</h2>
<ul class="leadership-aims__grid">
<li class="leadership-aims__card">
<span class="leadership-aims__icon material-symbols-outlined" aria-hidden="true">record_voice_over</span>
<p>All members of the NSC family should have a voice in it. All voices and comments are of merit, even if they seem to criticise. However, we seek to be positive in our interactions with our students, parents, other staff and visitors.</p>
</li>
<li class="leadership-aims__card">
<span class="leadership-aims__icon material-symbols-outlined" aria-hidden="true">verified</span>
<p>It is important to keep true to our values in all our interactions.</p>
</li>
<li class="leadership-aims__card">
<span class="leadership-aims__icon material-symbols-outlined" aria-hidden="true">diversity_3</span>
<p>All students should have the opportunity to get involved in student leadership in their time with us — by holding a formal role, getting involved in an event, or participating in consultations about their school.</p>
</li>
</ul>
</section>

<section class="leadership-roles" aria-labelledby="leadership-roles-title">
<h2 class="leadership-roles__title" id="leadership-roles-title">Leadership roles</h2>
<p class="leadership-roles__intro">Select a role below to read what it involves and how to apply.</p>
<div class="leadership-roles__list">

<details class="views-accordion" open>
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">shield</span>Anti-bullying Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Anti-bullying ambassadors are recruited annually by submitting a letter of interest. Students appointed may stay in their role or give up their post after a year. Once full, we hope to have 60 anti-bullying ambassadors across the age groups.</p>
<p>As we have more year groups in school, we hope to establish year 10 and 12 students as leaders. The group is overseen by an SSA and a senior leader.</p>
<p>Anti-bullying ambassadors undergo a half day training with representatives from the Diana Award. This teaches them:</p>
<ul>
<li>What bullying is.</li>
<li>How to recognise it.</li>
<li>How to support other students — both the bully and the victim.</li>
<li>How to deal with friendship issues.</li>
<li>How to recognise bullying and when to get more support.</li>
</ul>
<p>Their duties include:</p>
<ul>
<li>Logging incidents with a member of teaching staff.</li>
<li>Dealing with friendship issues.</li>
<li>Offering a drop-in service in the library at lunch time each day.</li>
<li>Offering support to address friendship issues.</li>
<li>Taking details of incidents and passing these on to their link staff.</li>
<li>Being a support for a young person who is upset, anxious or worried and offering them strategies and ideas to help.</li>
<li>Working with leaders to eradicate bullying.</li>
<li>Advertising and promoting their work in assemblies and around the school.</li>
<li>Collecting student opinions and views.</li>
</ul>
<p>Students are supported by staff members to do this role and never work alone.</p>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">palette</span>Art Committee Members</span></summary>
<div class="views-accordion__body">
<p>Art committee members are approached and asked to apply by the Head of Art. They meet regularly and are involved in:</p>
<ul>
<li>Creating art displays around the school.</li>
<li>Promoting art through competitions and activities.</li>
<li>Supporting in Primary art days.</li>
<li>Supporting at Open events.</li>
</ul>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">restaurant</span>Canteen Ambassadors</span></summary>
<div class="views-accordion__body">
<p>These students work with our chef to share the ideas and views of the students on the menus served, the way the lunch sessions run and promote competitions and new menus.</p>
<p>Students can apply to be a Canteen Ambassador at any time in the year via our letter of interest.</p>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">eco</span>Environment Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Our environment ambassadors are led by Miss Toley, our Head of Geography. Ambitious to continue the work of our original committee, who achieved our plastic free school status, they are working on ways that we can be more sustainable and environmentally friendly.</p>
<p>Students can apply to be an Environmental Ambassador at any time in the year via our letter of interest.</p>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">local_library</span>Library Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Our library ambassadors are a group of students who work with Mrs Wright, our Librarian. They:</p>
<ul>
<li>Manage the library at lunch time.</li>
<li>Sign in student users at lunch time.</li>
<li>Loan out books.</li>
<li>Collect returned books.</li>
<li>Create reading displays and help with competitions to encourage other students to get into reading.</li>
<li>Loan out games.</li>
<li>Oversee the use of the library computers at lunch time.</li>
<li>Help return books to the shelves.</li>
<li>Help recommend new books to the librarian.</li>
<li>Help the librarian to ensure that the Library is a safe quiet space for all.</li>
</ul>
<p>Students can apply to be a Library Ambassador at any time in the year via our letter of interest.</p>
<figure class="views-accordion__figure">
<img loading="lazy" decoding="async" width="1024" height="768" src="https://i0.wp.com/www.northstowesc.org/wp-content/uploads/2024/10/Library-Ambassadors.jpg?resize=1024%2C768&amp;ssl=1" alt="Library ambassadors at work in the school library"/>
</figure>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">groups</span>Junior Leadership Committee</span></summary>
<div class="views-accordion__body">
<p>The Junior Leadership team is an elected group from years 11 and 13. They represent the school's voice and oversee the work of the school council. They report directly to the Headteacher and meet with the Leadership team once a month.</p>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">theater_comedy</span>Performing Arts Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Our PA leaders are appointed by the Head of PA. These roles are given to students who have regularly attended after school clubs and have supported in lunchtime activities and whole school events.</p>
<p>PA leaders:</p>
<ul>
<li>Support in lunchtime clubs.</li>
<li>Lead events for other students.</li>
<li>Attend at least one PA club every week.</li>
<li>Take a lead role in supporting the Head of PA in the organisation of productions.</li>
</ul>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">forum</span>School Council</span></summary>
<div class="views-accordion__body">
<p>The school council is appointed at the start of each academic year. Students apply by submitting a letter of interest. If there are more applications than places, students go through a short interview. Students hold the post for one year.</p>
<p>The council meets after school every fortnight. They are responsible for:</p>
<ul>
<li>Collecting the views of students in all year groups.</li>
<li>Working to discuss the issues raised by students and then presenting these to the Headteacher or Senior Leadership Team.</li>
<li>Feeding back to the student body about what they said, and what they are doing to respond to the ideas.</li>
</ul>
<p>Minutes from the most recent school council meeting can be found on our <a href="../../about/parent-student-views.html">Parent and Student Views</a> page.</p>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">sports</span>Sports Leaders</span></summary>
<div class="views-accordion__body">
<p>Our Sports Leaders are appointed by the Head of PE. These roles are given to students who have regularly attended after school clubs and have supported in lunchtime activities and whole school events.</p>
<p>Sports leaders:</p>
<ul>
<li>Support in lunchtime clubs.</li>
<li>Lead events for other students.</li>
<li>Attend at least one sports club every week.</li>
<li>Officiate in matches.</li>
</ul>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">school</span>Subject Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Our Subject Ambassadors are appointed by the Head of each subject. These roles are given to students who have regularly attended after school clubs in the subject area or have shown a real aptitude or enthusiasm for the subject.</p>
<p>They:</p>
<ul>
<li>Support with subject area displays.</li>
<li>Promote the subject on Open Evenings and other similar events.</li>
<li>Promote competitions and help judge the results.</li>
<li>Are able to talk to visiting adults about individual subjects.</li>
</ul>
</div>
</details>

<details class="views-accordion">
<summary><span class="views-accordion__label"><span class="views-accordion__icon material-symbols-outlined" aria-hidden="true">directions_bike</span>Travel Ambassadors</span></summary>
<div class="views-accordion__body">
<p>Our Travel Ambassadors are a diligent group of students who help us to identify ways of making the route to school easier. They identify issues that we might not know about and work with the Headteacher on the travel plan. Our travel plan sets targets to reduce the amount of cars used to come to school as well as undertaking initiatives to support those who cycle to school.</p>
<p>Students can apply to be a travel ambassador at any time in the year via our letter of interest.</p>
</div>
</details>

</div>
</section>

<aside class="leadership-apply">
<span class="material-symbols-outlined" aria-hidden="true">edit_note</span>
<p>Many leadership roles can be applied for at any time by submitting a <strong>letter of interest</strong> to the school.</p>
</aside>
</div>'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    start = text.index('<div class="entry-content learning-stagger">')
    end = text.index("</article>", start)
    new_text = text[:start] + NEW_CONTENT + "\n" + text[end:]
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"Patched {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
