class EXP08 implements Runnable {
    Thread t;
    EXP08() {
       t = new Thread(this, "Demo Thread");
       System.out.println("Child thread: " + t);
       t.start(); // Start the thread
    }   
       public void run() {
       try {
          for(int i = 5; i > 0; i--) {
             System.out.println("Child Thread: " + i);
             
             Thread.sleep(50);
          }
      } catch (InterruptedException e) {
          System.out.println("Child interrupted.");
      }
      System.out.println("Exiting child thread.");
    }
 }
 
 public class ThreadDemo {
    public static void main(String args[]) {
       new EXP08(); 
       try {
          for(int i = 5; i > 0; i--) {
            System.out.println("Main Thread: " + i);
            Thread.sleep(100);
          }
       } catch (InterruptedException e) {
          System.out.println("Main thread interrupted.");
       }
       System.out.println("Main thread exiting.");
    }
 }