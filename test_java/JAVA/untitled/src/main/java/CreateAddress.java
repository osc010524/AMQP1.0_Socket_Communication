import org.apache.activemq.artemis.api.core.RoutingType;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.api.core.client.ServerLocator;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.SimpleString;

import java.util.EnumSet;

public class CreateAddress {
    public static void main(String[] args) {
        ServerLocator locator = null;
        ClientSession session = null;
        String address_name = "test_address8";
        try {
            // Create ServerLocator to connect to the broker
            locator = ActiveMQClient.createServerLocator("tcp://192.168.0.32:61616");

            // Set the timeouts to the maximum value
            locator.setConnectionTTL(Long.MAX_VALUE); // Max connection TTL
            locator.setCallTimeout(Long.MAX_VALUE);   // Max call timeout
            locator.setCallFailoverTimeout(Long.MAX_VALUE); // Max failover timeout

            // Create session factory and session
            session = locator.createSessionFactory().createSession();

            // Start session
            session.start();

            // Create Address with name "TestAddress"
            SimpleString addressName = new SimpleString(address_name);
            EnumSet<RoutingType> routingTypes = EnumSet.of(RoutingType.ANYCAST);
            session.createAddress(addressName, routingTypes, false);

            System.out.printf("Address '%s' created successfully.%n", addressName);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if (session != null) {
                    session.close();
                }
                if (locator != null) {
                    locator.close();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
