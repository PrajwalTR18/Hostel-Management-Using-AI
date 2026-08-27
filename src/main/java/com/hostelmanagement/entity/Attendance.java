package com.hostelmanagement.entity;
import jakarta.persistence.*; import lombok.*; import java.time.*;
@Entity @Getter @Setter @NoArgsConstructor @Table(uniqueConstraints=@UniqueConstraint(columnNames={"student_id","date"}))
public class Attendance { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @ManyToOne(optional=false) Student student; LocalDate date; boolean present; boolean late; }
