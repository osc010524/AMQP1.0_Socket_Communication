//import javax.jms.Connection;
//import javax.jms.ConnectionFactory;
//import javax.jms.Destination;
//import javax.jms.MessageProducer;
//import javax.jms.Session;
//import javax.jms.TextMessage;
//import javax.jms.JMSException;
//import javax.jms.Message;
//import javax.jms.Queue;
//
//import org.apache.activemq.ActiveMQConnectionFactory;
//
//public class JMSSender {
//
//    // ActiveMQ 브로커 URL
//    private static String brokerURL = "tcp://192.168.0.30:61616";
//    // 큐 이름
//    private static String queueName = "testQ3";
//
//    public static void main(String[] args) {
//        Connection connection = null;
//        try {
//            // ConnectionFactory 생성
//            ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(brokerURL);
//            // Connection 생성
//            connection = connectionFactory.createConnection();
//            connection.start();
//
//            // Session 생성 (트랜잭션 사용 여부, 자동 메시지 확인 모드)
//            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
//
//            // 큐 생성 또는 찾기
//            Queue queue = session.createQueue(queueName);
//
//            // Producer 생성
//            MessageProducer producer = session.createProducer(queue);
//            // 메시지 영구 저장 설정
//            producer.setDeliveryMode(Message.DEFAULT_DELIVERY_MODE); // DeliveryMode.PERSISTENT가 기본 설정임
//
//            // 메시지 생성
//            String messageText = "This is a persistent message!";
//            TextMessage message = session.createTextMessage(messageText);
//
//            // 메시지 전송
//            producer.send(message);
//            System.out.println("Sent message: " + message.getText());
//
//            // 자원 정리
//            producer.close();
//            session.close();
//        } catch (JMSException e) {
//            e.printStackTrace();
//        } finally {
//            if (connection != null) {
//                try {
//                    connection.close();
//                } catch (JMSException e) {
//                    e.printStackTrace();
//                }
//            }
//        }
//    }
//}
