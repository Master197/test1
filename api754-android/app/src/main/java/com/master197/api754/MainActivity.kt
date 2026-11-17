package com.master197.api754
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

data class Q(val key:String,val title:String,val help:String="",val options:List<String> = emptyList())
val qs = listOf(
 Q("site","Facility / site"), Q("unit","Process unit / area"), Q("event_id","Event / notification ID"),
 Q("assessor","Assessor"), Q("reviewer","Reviewer / process safety focal point"),
 Q("date","Event date (YYYY-MM-DD)"), Q("time","Event time / time zone"),
 Q("event_type","Event type",options=listOf("Unplanned / uncontrolled release","Fire or explosion","Injury / occupational event","Other / unknown")),
 Q("material","Material / substance", "Enter substance or mixture, if known."),
 Q("release","Was there an unplanned or uncontrolled release of material from a process?","Check the applicable API definitions.",listOf("Yes","No","Unknown")),
 Q("source","Release source / route",options=listOf("Process equipment / piping","Pressure relief device (PRD)","SIS / emergency depressuring","Upset emission from permitted / regulated source","Other / unknown")),
 Q("quantity","Estimated quantity released (kg)","Enter value or Unknown."),
 Q("duration","Estimated release duration (minutes)"),
 Q("employee","Employee / contractor / subcontractor fatality or days-away-from-work injury?",options=listOf("No","Yes","Unknown")),
 Q("thirdparty","Third-party hospital admission or fatality?",options=listOf("No","Yes","Unknown")),
 Q("community","Officially declared community evacuation or shelter-in-place?",options=listOf("No","Yes","Unknown")),
 Q("firecost","Direct fire / explosion damage cost","Enter numeric amount or Unknown."),
 Q("t1qty","Does quantity meet the applicable Tier 1 threshold?", "Check current licensed API table / material category.",listOf("No","Yes","Unknown","Not determined / N/A")),
 Q("prd1","PRD / SIS / emergency depressuring: qualifying Tier 1 consequence?",options=listOf("Not applicable","No","Yes","Unknown")),
 Q("upset1","Upset emission: qualifying Tier 1 consequence?",options=listOf("Not applicable","No","Yes","Unknown")),
 Q("special","Was a qualifying special-route consequence identified?","Verify rainout, unsafe discharge location, protective action and public measures against the standard.",listOf("No","Yes","Unknown","Not applicable")),
 Q("recordable","Recordable work-related injury (not already Tier 1)?",options=listOf("No","Yes","Unknown")),
 Q("t2qty","Does quantity meet the applicable Tier 2 threshold?",options=listOf("No","Yes","Unknown","Not determined / N/A")),
 Q("prd2","PRD / SIS / manual depressuring meets Tier 2 criteria?",options=listOf("No","Yes","Unknown","Not applicable")),
 Q("upset2","Upset emission meets Tier 2 criteria?",options=listOf("No","Yes","Unknown","Not applicable")),
 Q("currency","Cost currency",options=listOf("USD","EGP","EUR","GBP","SAR","AED")),
 Q("t1cost","Site-approved Tier 1 fire / explosion cost threshold","Enter threshold from controlled standard / company procedure."),
 Q("t2cost","Site-approved Tier 2 fire / explosion cost threshold","Enter threshold from controlled standard / company procedure."),
 Q("evidence","Evidence and references","SAP notification, operator log, historian trend, permit, medical report, estimate, release calculation."),
 Q("notes","Additional notes / assumptions"),
 Q("confirmed","Have current API RP 754 and site thresholds been checked?",options=listOf("Yes","No"))
)

class MainActivity:ComponentActivity(){
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState); setContent { Screen { a,r,why,open -> makeReport(a,r,why,open) } }}
 private fun makeReport(a:Map<String,String>, result:String, why:List<String>, open:List<String>){
  val dir=File(filesDir,"reports").apply{mkdirs()}
  val name=(a["event_id"]?.takeIf{it.isNotBlank()} ?: "assessment").replace(Regex("[^A-Za-z0-9_-]"),"_")
  val file=File(dir,"API754_PSE_$name.docx")
  val body=buildString {
   append("API RP 754 — PROCESS SAFETY EVENT SCREENING REPORT\nPRELIMINARY DECISION-SUPPORT RECORD — HUMAN REVIEW REQUIRED\n\nRESULT\n$result\n\nRATIONALE\n")
   why.forEach{append("• $it\n")}
   append("\nUNRESOLVED ITEMS\n"); if(open.isEmpty()) append("None identified by this screening.\n") else open.forEach{append("• $it\n")}
   append("\nEVENT DETAILS AND ALL ANSWERS\n")
   qs.forEach{q->append(q.title+": "+(a[q.key] ?: "")+"\n")}
   append("\nLIMITATIONS AND REVIEW\n")
   append("This is a preliminary screening aid, not an API-certified calculator or substitute for incident investigation, licensed current API RP 754 text, or approved company procedure. Chemical threshold tables and mixture calculations are not embedded. Cost thresholds must be entered and verified by the user. Unknown answers must not be assumed to mean No. Competent process-safety review is mandatory.\n")
   append("Reference basis: API Guide to Reporting Process Safety Events, Appendix C decision logic, subject to verification against the current licensed edition and corporate procedure.\n")
  }
  val paragraphs=body.split("\n").joinToString(""){line->"<w:p><w:r><w:t xml:space=\"preserve\">"+line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")+"</w:t></w:r></w:p>"}
  ZipOutputStream(FileOutputStream(file)).use{z->
   fun put(n:String,s:String){z.putNextEntry(ZipEntry(n));z.write(s.toByteArray(Charsets.UTF_8));z.closeEntry()}
   put("[Content_Types].xml","""<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>""")
   put("_rels/.rels","""<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>""")
   put("word/document.xml","""<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>$paragraphs<w:sectPr/></w:body></w:document>""")
  }
  val uri=FileProvider.getUriForFile(this,"$packageName.provider",file)
  val send=Intent(Intent.ACTION_SEND).apply{type="application/vnd.openxmlformats-officedocument.wordprocessingml.document";putExtra(Intent.EXTRA_STREAM,uri);putExtra(Intent.EXTRA_SUBJECT,"API RP 754 PSE Screening Report");addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)}
  startActivity(Intent.createChooser(send,"Save or share Word report"))
 }
}

@Composable fun Screen(onReport:(Map<String,String>,String,List<String>,List<String>)->Unit){
 val a=remember{mutableStateMapOf<String,String>()}; var i by remember{mutableIntStateOf(0)}; var done by remember{mutableStateOf(false)}
 val result=if(done) assess(a.toMap()) else Triple("", emptyList(), emptyList())
 MaterialTheme(colorScheme=lightColorScheme(primary=androidx.compose.ui.graphics.Color(0xFF14566F))){
  Scaffold{pad->Column(Modifier.fillMaxSize().padding(pad).padding(20.dp).verticalScroll(rememberScrollState())){
   Text("API RP 754",color=MaterialTheme.colorScheme.primary,style=MaterialTheme.typography.labelLarge)
   Text("Process Safety Event Screening",style=MaterialTheme.typography.headlineSmall,fontWeight=FontWeight.Bold)
   Spacer(Modifier.height(16.dp))
   if(!done){
    val q=qs[i]; val value=a[q.key].orEmpty()
    LinearProgressIndicator(progress={(i+1).toFloat()/qs.size},modifier=Modifier.fillMaxWidth())
    Text("Question "+(i+1)+" of "+qs.size,modifier=Modifier.padding(vertical=10.dp))
    Card(Modifier.fillMaxWidth()){Column(Modifier.padding(18.dp)){
     Text(q.title,style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.SemiBold)
     if(q.help.isNotBlank()){Spacer(Modifier.height(8.dp));Text(q.help,style=MaterialTheme.typography.bodySmall)}
     Spacer(Modifier.height(16.dp))
     if(q.options.isNotEmpty()) q.options.forEach{o->
      OutlinedButton(onClick={a[q.key]=o},modifier=Modifier.fillMaxWidth(),colors=ButtonDefaults.outlinedButtonColors(containerColor=if(value==o) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface)){Text(o,modifier=Modifier.fillMaxWidth())}
      Spacer(Modifier.height(5.dp))
     } else OutlinedTextField(value=value,onValueChange={a[q.key]=it},modifier=Modifier.fillMaxWidth(),label={Text("Your answer")},minLines=if(q.key=="evidence"||q.key=="notes")3 else 1)
    }}
    Spacer(Modifier.height(16.dp))
    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){
     OutlinedButton(onClick={if(i>0)i--},enabled=i>0){Text("Back")}
     Button(onClick={if(i<qs.lastIndex)i++ else done=true},enabled=value.isNotBlank()){Text(if(i==qs.lastIndex)"Assess event" else "Next")}
    }
    Text("Answers remain saved when moving back. Use Unknown / Not applicable rather than guessing.",style=MaterialTheme.typography.bodySmall,modifier=Modifier.padding(top=14.dp))
   }else{
    Text("Assessment result",style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold)
    Card(Modifier.fillMaxWidth().padding(top=10.dp)){Column(Modifier.padding(16.dp)){
     Text(result.first,style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
     Text("Rationale",fontWeight=FontWeight.SemiBold,modifier=Modifier.padding(top=12.dp));result.second.forEach{Text("• $it")}
     Text("Unresolved items",fontWeight=FontWeight.SemiBold,modifier=Modifier.padding(top=12.dp))
     if(result.third.isEmpty())Text("None identified by this screening.") else result.third.forEach{Text("• $it")}
    }}
    Button(onClick={onReport(a.toMap(),result.first,result.second,result.third)},modifier=Modifier.fillMaxWidth().padding(top=14.dp)){Text("Generate full Word report (.docx)")}
    OutlinedButton(onClick={done=false;i=0},modifier=Modifier.fillMaxWidth()){Text("Review / edit answers")}
    OutlinedButton(onClick={a.clear();done=false;i=0},modifier=Modifier.fillMaxWidth()){Text("Start new assessment")}
    Text("Preliminary screening only. Verify criteria against the current licensed API RP 754 edition and approved site procedure. Competent human review is mandatory.",color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall,modifier=Modifier.padding(top=12.dp))
   }
  }}
 }
}

private fun assess(a:Map<String,String>):Triple<String,List<String>,List<String>>{
 if(a["release"]=="No")return Triple("NOT TIER 1 OR TIER 2 — ENTRY CONDITION NOT MET",listOf("No unplanned or uncontrolled process release reported."),emptyList())
 if(a["release"]!="Yes")return Triple("HOLD — INSUFFICIENT INFORMATION",listOf("Process release entry condition is unknown."),listOf("Confirm whether an unplanned / uncontrolled process release occurred."))
 val t1=mutableListOf<String>();val t2=mutableListOf<String>();val u=mutableListOf<String>()
 if(a["employee"]=="Yes")t1.add("Employee / contractor / subcontractor fatality or days-away-from-work injury")
 if(a["thirdparty"]=="Yes")t1.add("Third-party hospital admission or fatality")
 if(a["community"]=="Yes")t1.add("Officially declared community evacuation / shelter-in-place")
 listOf("employee" to "Tier 1 injury / fatality status","thirdparty" to "Third-party hospital admission / fatality status","community" to "Community protective action status").forEach{if(a[it.first]=="Unknown"||a[it.first].isNullOrBlank())u.add(it.second)}
 val cost=a["firecost"]?.toDoubleOrNull();val c1=a["t1cost"]?.toDoubleOrNull();val c2=a["t2cost"]?.toDoubleOrNull()
 if(cost!=null&&c1!=null&&cost>0&&cost>=c1)t1.add("Fire / explosion damage cost meets entered Tier 1 threshold")
 if(a["t1qty"]=="Yes")t1.add("Release quantity meets applicable Tier 1 threshold (user-confirmed)")
 if(a["t1qty"]=="Unknown"||a["t1qty"]?.startsWith("Not")==true)u.add("Tier 1 chemical threshold / quantity assessment")
 if((a["prd1"]=="Yes"||a["upset1"]=="Yes")&&a["special"]=="Yes"&&a["t1qty"]=="Yes")t1.add("Special release route: qualifying consequence and Tier 1 quantity")
 if(a["prd1"]=="Unknown"||a["upset1"]=="Unknown"||a["special"]=="Unknown")u.add("Special release-route consequence assessment")
 if(t1.isNotEmpty())return Triple("TIER 1 PSE — PRELIMINARY",t1,u)
 if(u.isNotEmpty())return Triple("HOLD — INSUFFICIENT INFORMATION",listOf("No confirmed Tier 1 criterion identified; unresolved items remain."),u)
 if(a["recordable"]=="Yes")t2.add("Recordable work-related injury")
 if(cost!=null&&c2!=null&&cost>0&&cost>=c2)t2.add("Fire / explosion damage cost meets entered Tier 2 threshold")
 if(a["t2qty"]=="Yes")t2.add("Release quantity meets applicable Tier 2 threshold (user-confirmed)")
 if(a["prd2"]=="Yes")t2.add("PRD / SIS / manual depressuring release meets Tier 2 criteria")
 if(a["upset2"]=="Yes")t2.add("Upset emission meets Tier 2 criteria")
 listOf("recordable","t2qty","prd2","upset2").forEach{if(a[it]=="Unknown"||a[it].isNullOrBlank())u.add("Tier 2 criterion: $it")}
 if(t2.isNotEmpty())return Triple("TIER 2 PSE — PRELIMINARY",t2,u)
 if(u.isNotEmpty())return Triple("HOLD — INSUFFICIENT INFORMATION",listOf("No confirmed Tier 1 or Tier 2 criterion identified; unresolved items remain."),u)
 return Triple("NOT TIER 1 OR TIER 2 — VERIFY OTHER REPORTING",listOf("No Tier 1 or Tier 2 criterion identified from entered answers. Consider site-defined Tier 3 / other LOPC recording."),emptyList())
}
