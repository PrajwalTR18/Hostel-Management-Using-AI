package com.hostelmanagement.repository; import com.hostelmanagement.entity.Hostel; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface HostelRepository extends JpaRepository<Hostel,Long>{}
