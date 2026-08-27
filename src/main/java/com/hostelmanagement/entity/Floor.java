package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*;
@Entity @Getter @Setter @NoArgsConstructor
public class Floor { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; int floorNumber; @ManyToOne(optional=false) Block block; }
