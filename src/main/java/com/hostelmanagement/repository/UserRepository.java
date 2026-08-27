package com.hostelmanagement.repository; import com.hostelmanagement.entity.*; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface UserRepository extends JpaRepository<User,Long>{Optional<User> findByUsername(String username);}
