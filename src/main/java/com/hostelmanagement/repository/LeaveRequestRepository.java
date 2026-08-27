package com.hostelmanagement.repository; import com.hostelmanagement.entity.LeaveRequest; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface LeaveRequestRepository extends JpaRepository<LeaveRequest,Long>{}
