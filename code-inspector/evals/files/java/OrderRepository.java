package evals.files.java;

import java.util.List;

public interface OrderRepository {
    List<Order> findByUserId(long userId);
}
