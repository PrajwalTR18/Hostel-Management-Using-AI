package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*; import java.time.*;
@Entity @Getter @Setter @NoArgsConstructor
public class LeaveRequest { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @ManyToOne(optional=false) Student student; LocalDate startDate,endDate; String reason; @Enumerated(EnumType.STRING) Status status=Status.PENDING; String remarks; enum Status{PENDING,APPROVED,REJECTED,COMPLETED} }
