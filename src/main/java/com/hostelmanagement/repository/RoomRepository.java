package com.hostelmanagement.repository; import com.hostelmanagement.entity.Room; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface RoomRepository extends JpaRepository<Room,Long>{}
