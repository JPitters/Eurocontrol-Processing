package net.fliteplan.eurocontrol.beans;

import com.fasterxml.jackson.core.JsonProcessingException;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;

import org.springframework.context.annotation.Configuration;
import com.cfar.swim.aixm.*;

import java.io.StringReader;
import java.util.List;

@Configuration
public class AIXMDataToJava {
	private JAXBContext jaxbContext;

    public AIXMDataToJava() throws JAXBException {
        this.jaxbContext = JAXBContext.newInstance(Navaid.class);
    }
    
    public List<Navaid> message(String xml) throws JAXBException, JsonProcessingException {

        Unmarshaller jaxbUnmarshaller = jaxbContext.createUnmarshaller();
        Navaid aixms = (Navaid) jaxbUnmarshaller.unmarshal(new StringReader(xml));

        List<Navaid> navaids = null;
        
        return navaids;
    }
}
