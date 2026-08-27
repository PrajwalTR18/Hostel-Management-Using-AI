package com.hostelmanagement.repository; import com.hostelmanagement.entity.Complaint; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface ComplaintRepository extends JpaRepository<Complaint,Long>{}
