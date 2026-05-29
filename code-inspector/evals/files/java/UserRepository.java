package evals.files.java;

import java.util.List;

public interface UserRepository {
    List<User> findActiveUsers();
}
