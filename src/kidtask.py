import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

public class KidTaskApp {

    // --- 1. Data Models ---

    enum TaskStatus { PENDING, COMPLETED, APPROVED }
    enum WishStatus { REQUESTED, APPROVED, REDEEMED }
    enum UserRole { CHILD, PARENT, TEACHER }

    static class Task {
        String id;
        String title;
        String description;
        int points;
        TaskStatus status;
        int rating; 
        String addedBy; 

        public Task(String id, String title, String desc, int points, TaskStatus status, int rating, String addedBy) {
            this.id = id;
            this.title = title;
            this.description = desc;
            this.points = points;
            this.status = status;
            this.rating = rating;
            this.addedBy = addedBy;
        }

        public String toCSV() {
            return id + "," + title + "," + description + "," + points + "," + status + "," + rating + "," + addedBy;
        }

        public static Task fromCSV(String line) {
            String[] parts = line.split(",");
            return new Task(parts[0], parts[1], parts[2], Integer.parseInt(parts[3]), 
                            TaskStatus.valueOf(parts[4]), Integer.parseInt(parts[5]), parts[6]);
        }
    }

    static class Wish {
        String id;
        String name;
        int cost;
        int minLevel;
        WishStatus status;

        public Wish(String id, String name, int cost, int minLevel, WishStatus status) {
            this.id = id;
            this.name = name;
            this.cost = cost;
            this.minLevel = minLevel;
            this.status = status;
        }

        public String toCSV() {
            return id + "," + name + "," + cost + "," + minLevel + "," + status;
        }

        public static Wish fromCSV(String line) {
            String[] parts = line.split(",");
            return new Wish(parts[0], parts[1], Integer.parseInt(parts[2]), 
                            Integer.parseInt(parts[3]), WishStatus.valueOf(parts[4]));
        }
    }

    static class ChildStats {
        int currentPoints = 0; 
        int totalPointsEarned = 0; 
        
        public int getLevel() {
            return 1 + (totalPointsEarned / 50); 
        }
    }

    // --- 2. Data Manager (Persistence) ---

    static class DataManager {
        private static final String TASK_FILE = "tasks.csv";
        private static final String WISH_FILE = "wishes.csv";
        private static final String STATS_FILE = "user_stats.csv";

        public static List<Task> loadTasks() {
            List<Task> tasks = new ArrayList<>();
            File file = new File(TASK_FILE);
            if (!file.exists()) return tasks;
            
            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = br.readLine()) != null) {
                    if(!line.trim().isEmpty()) tasks.add(Task.fromCSV(line));
                }
            } catch (IOException e) { e.printStackTrace(); }
            return tasks;
        }

        public static void saveTasks(List<Task> tasks) {
            try (PrintWriter pw = new PrintWriter(new FileWriter(TASK_FILE))) {
                for (Task t : tasks) pw.println(t.toCSV());
            } catch (IOException e) { e.printStackTrace(); }
        }

        public static List<Wish> loadWishes() {
            List<Wish> wishes = new ArrayList<>();
            File file = new File(WISH_FILE);
            if (!file.exists()) return wishes;

            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = br.readLine()) != null) {
                    if(!line.trim().isEmpty()) wishes.add(Wish.fromCSV(line));
                }
            } catch (IOException e) { e.printStackTrace(); }
            return wishes;
        }

        public static void saveWishes(List<Wish> wishes) {
            try (PrintWriter pw = new PrintWriter(new FileWriter(WISH_FILE))) {
                for (Wish w : wishes) pw.println(w.toCSV());
            } catch (IOException e) { e.printStackTrace(); }
        }

        public static ChildStats loadStats() {
            ChildStats stats = new ChildStats();
            File file = new File(STATS_FILE);
            if (!file.exists()) return stats;

            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line = br.readLine();
                if (line != null) {
                    String[] parts = line.split(",");
                    stats.currentPoints = Integer.parseInt(parts[0]);
                    stats.totalPointsEarned = Integer.parseInt(parts[1]);
                }
            } catch (IOException e) { e.printStackTrace(); }
            return stats;
        }

        public static void saveStats(ChildStats stats) {
            try (PrintWriter pw = new PrintWriter(new FileWriter(STATS_FILE))) {
                pw.println(stats.currentPoints + "," + stats.totalPointsEarned);
            } catch (IOException e) { e.printStackTrace(); }
        }
    }

    // --- 3. GUI Application ---

    private JFrame frame;
    private JPanel mainPanel;
    private CardLayout cardLayout;
    
    private UserRole currentRole;
    private List<Task> tasks;
    private List<Wish> wishes;
    private ChildStats stats;

    private JLabel lblPoints;
    private JProgressBar progressLevel;
    private JTable taskTable;
    private DefaultTableModel taskModel;
    private JTable wishTable;
    private DefaultTableModel wishModel;

    public KidTaskApp() {
        tasks = DataManager.loadTasks();
        wishes = DataManager.loadWishes();
        stats = DataManager.loadStats();

        initializeUI();
    }

    private void initializeUI() {
        frame = new JFrame("KidTask - Task & Wish Manager");
        frame.setSize(900, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLocationRelativeTo(null);

        cardLayout = new CardLayout();
        mainPanel = new JPanel(cardLayout);

        mainPanel.add(createLoginPanel(), "LOGIN");
        mainPanel.add(createDashboardPanel(), "DASHBOARD");

        frame.add(mainPanel);
        frame.setVisible(true);
    }

    // --- 3.1 Login Screen ---

    private JPanel createLoginPanel() {
        JPanel panel = new JPanel(new GridBagLayout());
        panel.setBackground(new Color(230, 240, 255));

        JLabel title = new JLabel("Welcome to KidTask");
        title.setFont(new Font("Arial", Font.BOLD, 28));
        
        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 20));
        btnPanel.setOpaque(false);

        JButton btnChild = createStyledButton("Child", new Color(100, 200, 100));
        JButton btnParent = createStyledButton("Parent", new Color(100, 150, 200));
        JButton btnTeacher = createStyledButton("Teacher", new Color(200, 100, 100));

        btnChild.addActionListener(e -> login(UserRole.CHILD));
        btnParent.addActionListener(e -> login(UserRole.PARENT));
        btnTeacher.addActionListener(e -> login(UserRole.TEACHER));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0; gbc.gridy = 0;
        gbc.insets = new Insets(0, 0, 30, 0);
        panel.add(title, gbc);
        
        gbc.gridy = 1;
        btnPanel.add(btnChild);
        btnPanel.add(btnParent);
        btnPanel.add(btnTeacher);
        panel.add(btnPanel, gbc);

        return panel;
    }

    private JButton createStyledButton(String text, Color bg) {
        JButton btn = new JButton(text);
        btn.setPreferredSize(new Dimension(120, 50));
        btn.setBackground(bg);
        btn.setForeground(Color.WHITE);
        btn.setFont(new Font("Arial", Font.BOLD, 14));
        btn.setFocusPainted(false);
        return btn;
    }

    private void login(UserRole role) {
        this.currentRole = role;
        refreshDashboard();
        cardLayout.show(mainPanel, "DASHBOARD");
    }

    private void logout() {
        DataManager.saveTasks(tasks);
        DataManager.saveWishes(wishes);
        DataManager.saveStats(stats);
        cardLayout.show(mainPanel, "LOGIN");
    }

    // --- 3.2 Main Dashboard ---

    private JPanel createDashboardPanel() {
        JPanel dashboard = new JPanel(new BorderLayout());

        JPanel header = new JPanel(new BorderLayout());
        header.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        header.setBackground(Color.WHITE);

        JLabel lblTitle = new JLabel("KidTask Dashboard");
        lblTitle.setFont(new Font("Arial", Font.BOLD, 20));
        
        JButton btnLogout = new JButton("Logout");
        btnLogout.addActionListener(e -> logout());

        header.add(lblTitle, BorderLayout.WEST);
        header.add(btnLogout, BorderLayout.EAST);

        JPanel statsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 20, 5));
        statsPanel.setBackground(new Color(245, 245, 245));
        lblPoints = new JLabel("Points: 0");
        lblPoints.setFont(new Font("Arial", Font.BOLD, 14));
        
        progressLevel = new JProgressBar(0, 50); 
        progressLevel.setStringPainted(true);
        progressLevel.setPreferredSize(new Dimension(200, 20));

        statsPanel.add(lblPoints);
        statsPanel.add(new JLabel("Level Progress:"));
        statsPanel.add(progressLevel);
        
        JPanel topContainer = new JPanel(new BorderLayout());
        topContainer.add(header, BorderLayout.NORTH);
        topContainer.add(statsPanel, BorderLayout.SOUTH);

        dashboard.add(topContainer, BorderLayout.NORTH);

        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("Task Management", createTaskTab());
        tabs.addTab("Wish Management", createWishTab());
        
        dashboard.add(tabs, BorderLayout.CENTER);

        return dashboard;
    }

    // --- 3.3 Task Tab ---

    private JPanel createTaskTab() {
        JPanel panel = new JPanel(new BorderLayout());
        
        String[] cols = {"ID", "Title", "Desc", "Points", "Status", "Rating", "Added By"};
        taskModel = new DefaultTableModel(cols, 0) {
            public boolean isCellEditable(int row, int column) { return false; }
        };
        taskTable = new JTable(taskModel);
        panel.add(new JScrollPane(taskTable), BorderLayout.CENTER);

        JPanel actionPanel = new JPanel();
        
        JButton btnAdd = new JButton("Add Task");
        JButton btnComplete = new JButton("Mark Completed");
        JButton btnRate = new JButton("Approve & Rate");

        btnAdd.addActionListener(e -> showAddTaskDialog());
        btnComplete.addActionListener(e -> markTaskCompleted());
        btnRate.addActionListener(e -> showRateTaskDialog());

        actionPanel.add(btnAdd);
        actionPanel.add(btnComplete);
        actionPanel.add(btnRate);
        
        panel.add(actionPanel, BorderLayout.SOUTH);
        return panel;
    }

    // --- 3.4 Wish Tab ---

    private JPanel createWishTab() {
        JPanel panel = new JPanel(new BorderLayout());

        String[] cols = {"ID", "Item", "Cost", "Min Level", "Status"};
        wishModel = new DefaultTableModel(cols, 0) {
            public boolean isCellEditable(int row, int column) { return false; }
        };
        wishTable = new JTable(wishModel);
        panel.add(new JScrollPane(wishTable), BorderLayout.CENTER);

        JPanel actionPanel = new JPanel();
        JButton btnAddWish = new JButton("Add Wish");
        JButton btnApproveWish = new JButton("Approve Wish");
        JButton btnRedeem = new JButton("Redeem");

        btnAddWish.addActionListener(e -> showAddWishDialog());
        btnApproveWish.addActionListener(e -> approveWish());
        btnRedeem.addActionListener(e -> redeemWish());

        actionPanel.add(btnAddWish);
        actionPanel.add(btnApproveWish);
        actionPanel.add(btnRedeem);

        panel.add(actionPanel, BorderLayout.SOUTH);
        return panel;
    }

    // --- 4. Logic & Dialogs ---

    private void refreshDashboard() {
        lblPoints.setText("Points: " + stats.currentPoints + " | Level: " + stats.getLevel());
        int progress = stats.totalPointsEarned % 50;
        progressLevel.setValue(progress);
        progressLevel.setString("Level " + stats.getLevel() + " (" + progress + "/50)");

        taskModel.setRowCount(0);
        for (Task t : tasks) {
            taskModel.addRow(new Object[]{t.id, t.title, t.description, t.points, t.status, 
                (t.rating > 0 ? t.rating : "-"), t.addedBy});
        }

        wishModel.setRowCount(0);
        for (Wish w : wishes) {
            if (currentRole == UserRole.CHILD && w.minLevel > stats.getLevel()) continue;
            wishModel.addRow(new Object[]{w.id, w.name, w.cost, w.minLevel, w.status});
        }
    }

    private void showAddTaskDialog() {
        if (currentRole == UserRole.CHILD) {
            JOptionPane.showMessageDialog(frame, "Only Parents or Teachers can add tasks.");
            return;
        }

        JTextField titleField = new JTextField();
        JTextField descField = new JTextField();
        JTextField pointsField = new JTextField();

        Object[] message = {
            "Title:", titleField,
            "Description:", descField,
            "Points:", pointsField
        };

        int option = JOptionPane.showConfirmDialog(frame, message, "Add New Task", JOptionPane.OK_CANCEL_OPTION);
        if (option == JOptionPane.OK_OPTION) {
            try {
                String title = titleField.getText();
                String desc = descField.getText();
                int pts = Integer.parseInt(pointsField.getText());
                String id = "T" + (tasks.size() + 1);
                
                String addedBy = (currentRole == UserRole.PARENT) ? "Parent" : "Teacher";
                tasks.add(new Task(id, title, desc, pts, TaskStatus.PENDING, 0, addedBy));
                DataManager.saveTasks(tasks);
                refreshDashboard();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(frame, "Invalid input. Please try again.");
            }
        }
    }

    private void markTaskCompleted() {
        if (currentRole != UserRole.CHILD) {
            JOptionPane.showMessageDialog(frame, "Only the child can mark tasks as done.");
            return;
        }
        int row = taskTable.getSelectedRow();
        if (row == -1) return;
        
        String id = (String) taskModel.getValueAt(row, 0);
        for (Task t : tasks) {
            if (t.id.equals(id) && t.status == TaskStatus.PENDING) {
                t.status = TaskStatus.COMPLETED;
                DataManager.saveTasks(tasks);
                refreshDashboard();
                return;
            }
        }
        JOptionPane.showMessageDialog(frame, "Task is not Pending.");
    }

    private void showRateTaskDialog() {
        if (currentRole == UserRole.CHILD) {
            JOptionPane.showMessageDialog(frame, "Children cannot approve tasks.");
            return;
        }
        int row = taskTable.getSelectedRow();
        if (row == -1) return;

        String id = (String) taskModel.getValueAt(row, 0);
        Task selectedTask = null;
        for (Task t : tasks) if (t.id.equals(id)) selectedTask = t;

        if (selectedTask == null || selectedTask.status != TaskStatus.COMPLETED) {
            JOptionPane.showMessageDialog(frame, "Only COMPLETED tasks can be approved.");
            return;
        }

        String ratingStr = JOptionPane.showInputDialog(frame, "Rate this task (1-5 stars):");
        if (ratingStr != null) {
            try {
                int rating = Integer.parseInt(ratingStr);
                if (rating < 1 || rating > 5) throw new Exception();
                
                selectedTask.status = TaskStatus.APPROVED;
                selectedTask.rating = rating;
                
                stats.currentPoints += selectedTask.points;
                stats.totalPointsEarned += selectedTask.points;
                
                DataManager.saveTasks(tasks);
                DataManager.saveStats(stats);
                refreshDashboard();
                JOptionPane.showMessageDialog(frame, "Task Approved! Points added.");
            } catch (Exception e) {
                JOptionPane.showMessageDialog(frame, "Invalid rating (1-5).");
            }
        }
    }

    private void showAddWishDialog() {
        if (currentRole != UserRole.CHILD) {
            JOptionPane.showMessageDialog(frame, "Only the child can request wishes.");
            return;
        }

        JTextField nameField = new JTextField();
        JTextField costField = new JTextField();

        Object[] message = { "Wish Item:", nameField, "Cost (Points):", costField };

        int option = JOptionPane.showConfirmDialog(frame, message, "Make a Wish", JOptionPane.OK_CANCEL_OPTION);
        if (option == JOptionPane.OK_OPTION) {
            try {
                String name = nameField.getText();
                int cost = Integer.parseInt(costField.getText());
                String id = "W" + (wishes.size() + 1);
                
                wishes.add(new Wish(id, name, cost, stats.getLevel(), WishStatus.REQUESTED));
                DataManager.saveWishes(wishes);
                refreshDashboard();
            } catch (Exception e) {
                JOptionPane.showMessageDialog(frame, "Invalid Input");
            }
        }
    }

    private void approveWish() {
        if (currentRole != UserRole.PARENT) {
            JOptionPane.showMessageDialog(frame, "Only Parents can approve wishes.");
            return;
        }
        int row = wishTable.getSelectedRow();
        if (row == -1) return;
        
        String id = (String) wishModel.getValueAt(row, 0);
        for (Wish w : wishes) {
            if (w.id.equals(id) && w.status == WishStatus.REQUESTED) {
                w.status = WishStatus.APPROVED;
                DataManager.saveWishes(wishes);
                refreshDashboard();
                JOptionPane.showMessageDialog(frame, "Wish Approved! Child can now redeem it.");
                return;
            }
        }
    }

    private void redeemWish() {
        if (currentRole != UserRole.CHILD) {
            JOptionPane.showMessageDialog(frame, "Only the child can redeem wishes.");
            return;
        }
        int row = wishTable.getSelectedRow();
        if (row == -1) return;

        String id = (String) wishModel.getValueAt(row, 0);
        for (Wish w : wishes) {
            if (w.id.equals(id)) {
                if (w.status != WishStatus.APPROVED) {
                    JOptionPane.showMessageDialog(frame, "Wish must be APPROVED by parent first.");
                    return;
                }
                if (stats.currentPoints >= w.cost) {
                    w.status = WishStatus.REDEEMED;
                    stats.currentPoints -= w.cost;
                    DataManager.saveWishes(wishes);
                    DataManager.saveStats(stats);
                    refreshDashboard();
                    JOptionPane.showMessageDialog(frame, "Wish Redeemed! Enjoy!");
                } else {
                    JOptionPane.showMessageDialog(frame, "Not enough points!");
                }
                return;
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(KidTaskApp::new);
    }
}