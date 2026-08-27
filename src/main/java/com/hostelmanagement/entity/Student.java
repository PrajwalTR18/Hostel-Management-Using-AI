package com.hostelmanagement.entity;
import jakarta.persistence.*; import jakarta.validation.constraints.*; import lombok.*;
@Entity @Getter @Setter @NoArgsConstructor
public class Student { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @Column(nullable=false,unique=true) String studentId; @Column(nullable=false) String name; @Email @Column(nullable=false,unique=true) String email; String phone; String gender; String course; String department; Integer year; Integer semester; String address; String guardianName; String guardianPhone; String emergencyContact; @ManyToOne Room room; boolean active=true; }
