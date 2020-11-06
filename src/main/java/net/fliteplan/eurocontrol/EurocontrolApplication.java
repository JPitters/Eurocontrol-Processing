package net.fliteplan.eurocontrol;

import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import javax.sql.DataSource;
import javax.xml.bind.annotation.*;
import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;


import net.fliteplan.eurocontrol.beans.AIXMDataToJava;
import org.apache.camel.builder.RouteBuilder;

@SpringBootApplication
public class EurocontrolApplication extends RouteBuilder  {

	public static void main(String[] args) {
		SpringApplication.run(EurocontrolApplication.class, args);
	}
	
	@Autowired
	DataSource dataSource;
	
	public DataSource getDataSource() {
		return dataSource;
	}

	public void setDataSource(DataSource dataSource) {
		this.dataSource = dataSource;
	}
	
	@Autowired
	AIXMDataToJava msgSplitter;
	
	@Value("${tfms.filepath}")
	private String jumpStartLogFilesPath;

	@Value("${tfms.pollmsec:100000}")
	private BigInteger pollDelayMilliSeconds;

	@Value("${tfms.deletefiles:true}")
	private Boolean deleteOnRead;
	
	@Override
	public void configure() throws Exception {
		
		String pollDelayStr = "?delay=" + pollDelayMilliSeconds.toString();
		String deleteStr = "&delete=" + deleteOnRead.toString();
		
		Path path = Paths.get(jumpStartLogFilesPath);
		if(!Files.isDirectory(path)) {
			System.out.println(jumpStartLogFilesPath + " is not a valid directory path");
		}
		
		//System.out.println("Beginning Camel route");
		errorHandler(deadLetterChannel("log:dead?level=ERROR"));

		//from("file:xml-in")
		
	}

}
