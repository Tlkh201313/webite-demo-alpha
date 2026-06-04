"""Replace broken attendance staff tables with structured markup."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "nsc-life" / "attendance.html"
text = path.read_text(encoding="utf-8")

start_marker = '<p class="wp-block-paragraph">Further details about government policy'
end_marker = '<div style="height:25px" aria-hidden="true" class="wp-block-spacer"></div>'

start = text.find(start_marker)
end = text.find(end_marker, start)
if start == -1 or end == -1:
    raise SystemExit(f"markers not found: start={start} end={end}")

replacement = """<p class="wp-block-paragraph">Further details about government policy and advice on this matter is available at <a href="https://www.gov.uk/school-attendance-absence/help-with-getting-your-child-to-go-to-school">help with getting your child to go to school</a>.</p>



<p class="wp-block-paragraph">Meridian Trust <a href="https://www.meridiantrust.co.uk/key-information/attendance/">Attendance and Support Information</a></p>



<p class="wp-block-paragraph">External support and resources: <a href="feeling-worried-or-anxious.html">Feeling worried or anxious?</a></p>



<section class="attendance-staff" id="attendance-staff">
<h2 class="attendance-staff__title">Attendance staff &#8211; Meridian Trust and Northstowe Secondary College</h2>

<div class="attendance-staff__group">
<h3 class="attendance-staff__group-title">Trust attendance staff</h3>
<div class="nsc-table-wrap">
<table class="nsc-data-table">
<thead>
<tr>
<th scope="col">Name</th>
<th scope="col">Title</th>
<th scope="col">Designated Safeguarding Lead trained (DSL)</th>
<th scope="col">Email contact</th>
</tr>
</thead>
<tbody>
<tr>
<td>Sharon Templeman</td>
<td>Trust Attendance Welfare Leader</td>
<td class="nsc-cell--yesno">Yes</td>
<td><a href="mailto:stempleman@meridiantrust.co.uk">stempleman@meridiantrust.co.uk</a></td>
</tr>
<tr>
<td>Martin Campbell</td>
<td>Executive Principal</td>
<td class="nsc-cell--yesno">Yes</td>
<td><a href="mailto:mcampbell@merdiantrust.co.uk">mcampbell@merdiantrust.co.uk</a></td>
</tr>
</tbody>
</table>
</div>
</div>

<div class="attendance-staff__group">
<h3 class="attendance-staff__group-title">Northstowe Secondary College attendance staff</h3>
<div class="nsc-table-wrap">
<table class="nsc-data-table">
<thead>
<tr>
<th scope="col">Name</th>
<th scope="col">Title</th>
<th scope="col">DSL trained</th>
<th scope="col">Email contact</th>
</tr>
</thead>
<tbody>
<tr>
<td>Claire Mills</td>
<td>Principal</td>
<td class="nsc-cell--yesno">Yes</td>
<td><a href="mailto:Head@northstowe.education">Head@northstowe.education</a></td>
</tr>
<tr>
<td>Carl Deighton</td>
<td>Attendance Lead (SLT)</td>
<td class="nsc-cell--yesno">Yes</td>
<td><a href="mailto:CDeighton@northstowe.education">CDeighton@northstowe.education</a></td>
</tr>
<tr>
<td>Nicky Tabb</td>
<td>Attendance Officer</td>
<td class="nsc-cell--yesno">No</td>
<td><a href="mailto:NTabb@northstowe.education">NTabb@northstowe.education</a></td>
</tr>
<tr>
<td>Simon Russell</td>
<td>Designated Safeguarding Lead (DSL)</td>
<td class="nsc-cell--yesno">Yes</td>
<td><a href="mailto:SRussell@Northstowe.education">SRussell@Northstowe.education</a></td>
</tr>
<tr>
<td>Sarah Middleton</td>
<td>Academy Councillor</td>
<td class="nsc-cell--yesno">No</td>
<td><a href="mailto:smiddleton@gov.northstowe.education">smiddleton@gov.northstowe.education</a></td>
</tr>
</tbody>
</table>
</div>
</div>

<div class="attendance-staff__group">
<h3 class="attendance-staff__group-title">Staff responsible for daily attendance reporting</h3>
<div class="nsc-table-wrap">
<table class="nsc-data-table">
<thead>
<tr>
<th scope="col">Name</th>
<th scope="col">Title</th>
<th scope="col">House / year / crew</th>
<th scope="col">Email contact</th>
<th scope="col">Tel number</th>
</tr>
</thead>
<tbody>
<tr>
<td>Caroline Cook</td>
<td>Student Support Assistant &amp; Attendance</td>
<td>Attenborough</td>
<td><a href="mailto:CCook@northstowe.education">CCook@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343806</td>
</tr>
<tr>
<td>Debbie Pitt</td>
<td>Student Support Assistant</td>
<td>Dyson</td>
<td><a href="mailto:DPitt@northstowe.education">DPitt@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343728</td>
</tr>
<tr>
<td>Clare Wadd</td>
<td>Student Support Assistant</td>
<td>Glennie</td>
<td><a href="mailto:CWadd@northstowe.education">CWadd@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343736</td>
</tr>
<tr>
<td>Louise Bucknall</td>
<td>Student Support Assistant</td>
<td>Parks</td>
<td><a href="mailto:LBucknall@northstowe.education">LBucknall@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343809</td>
</tr>
<tr>
<td>Hannah Matthews</td>
<td>Senior Tutor</td>
<td>Attenborough</td>
<td><a href="mailto:HMatthews@Northstowe.education">HMatthews@Northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343800</td>
</tr>
<tr>
<td>Hope Noble</td>
<td>Senior Tutor</td>
<td>Dyson</td>
<td><a href="mailto:HNoble@northstowe.education">HNoble@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343800</td>
</tr>
<tr>
<td>Anthony Williams</td>
<td>Senior Tutor</td>
<td>Glennie</td>
<td><a href="mailto:AWilliams@northstowe.education">AWilliams@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343800</td>
</tr>
<tr>
<td>Anne Steventon</td>
<td>Senior Tutor</td>
<td>Parks</td>
<td><a href="mailto:ASteventon@northstowe.education">ASteventon@northstowe.education</a></td>
<td class="nsc-cell--tel">01223 343800</td>
</tr>
</tbody>
</table>
</div>
</div>

<ul class="attendance-staff__links">
<li><a href="https://www.cambridgeshire.gov.uk/residents/children-and-families/schools-learning/education-your-rights-and-responsibilities/non-attendance-and-the-law">Local Authority Penalty Notice Code of Conduct</a></li>
<li><a href="https://www.meridiantrust.co.uk/key-information/policies/">Trust Attendance Policy</a></li>
<li><a href="https://www.meridiantrust.co.uk/key-information/attendance/">Trust Parent Attendance Support Information</a></li>
</ul>
</section>



"""

path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")
print(f"Patched {path.relative_to(ROOT)}")
