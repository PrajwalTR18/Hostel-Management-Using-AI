package com.hostelmanagement;
import com.hostelmanagement.ai.ComplaintAnalysisService; import org.junit.jupiter.api.Test; import static org.junit.jupiter.api.Assertions.*;
class ComplaintAnalysisServiceTest { @Test void classifiesPlumbing(){var r=new ComplaintAnalysisService().analyze("Water is leaking continuously from the bathroom pipe."); assertEquals("Plumbing",r.get("category")); assertEquals("HIGH",r.get("priority"));} }
