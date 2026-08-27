package com.hostelmanagement.repository; import com.hostelmanagement.entity.Attendance; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface AttendanceRepository extends JpaRepository<Attendance,Long>{}
