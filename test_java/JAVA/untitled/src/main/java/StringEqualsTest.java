public class StringEqualsTest {

    public static void main(String[] args) {
        // Create instances of String to test
        String str1 = "hello";
        String str2 = "hello";
        String str3 = new String("hello"); // Different object, same value
        String str4 = "world";

        // Test cases
        System.out.println("str1.equals(str1): " + str1.equals(str1)); // Should be true, same object
        System.out.println("str1.equals(str2): " + str1.equals(str2)); // Should be true, same value and same string pool object
        System.out.println("str1.equals(str3): " + str1.equals(str3)); // Should be true, same value but different object
        System.out.println("str1.equals(str4): " + str1.equals(str4)); // Should be false, different value
        System.out.println("str1.equals(null): " + str1.equals(null)); // Should be false, comparing with null
    }

    public boolean equals(Object anObject) {
        if (this == anObject) {
            return true;
        } else {
            if (anObject instanceof String) {
                String aString = (String)anObject;
                if (this.coder() == aString.coder()) {
                    return this.isLatin1() ? StringLatin1.equals(this.value, aString.value) : StringUTF16.equals(this.value, aString.value);
                }
            }

            return false;
        }
    }
}
