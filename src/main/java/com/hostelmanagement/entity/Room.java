package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*;
@Entity @Getter @Setter @NoArgsConstructor
public class Room { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @Column(nullable=false,unique=true) String roomNumber; String roomType; int capacity; int occupiedBeds; @Enumerated(EnumType.STRING) RoomStatus status=RoomStatus.AVAILABLE; @ManyToOne(optional=false) Floor floor; public int availableBeds(){return Math.max(0,capacity-occupiedBeds);} }
