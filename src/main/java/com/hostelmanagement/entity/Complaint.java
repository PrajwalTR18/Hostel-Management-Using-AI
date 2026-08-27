package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*; import java.time.*;
@Entity @Getter @Setter @NoArgsConstructor
public class Complaint { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @ManyToOne(optional=false) Student student; String category; @Column(length=2000,nullable=false) String description; String location; @Enumerated(EnumType.STRING) Priority priority=Priority.MEDIUM; @Enumerated(EnumType.STRING) ComplaintStatus status=ComplaintStatus.SUBMITTED; String assignedDepartment; String aiSummary; String sentiment; String suggestedAction; LocalDateTime createdAt=LocalDateTime.now(); LocalDateTime resolvedAt; String remarks; }
