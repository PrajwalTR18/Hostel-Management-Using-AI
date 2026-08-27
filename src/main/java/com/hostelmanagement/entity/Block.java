package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*;
@Entity @Getter @Setter @NoArgsConstructor
public class Block { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @Column(nullable=false) String name; @ManyToOne(optional=false) Hostel hostel; }
