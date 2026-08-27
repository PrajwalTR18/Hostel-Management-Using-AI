package com.hostelmanagement.repository; import com.hostelmanagement.entity.Student; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface StudentRepository extends JpaRepository<Student,Long>{}
