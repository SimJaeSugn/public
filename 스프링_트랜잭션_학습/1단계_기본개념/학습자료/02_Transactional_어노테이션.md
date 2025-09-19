# @Transactional 어노테이션 상세 가이드

## 1. @Transactional 어노테이션 개요

### 기본 개념
`@Transactional`은 스프링에서 제공하는 어노테이션으로, 메서드나 클래스에 적용하여 트랜잭션을 자동으로 관리할 수 있게 해줍니다.

### 주요 특징
- **선언적 트랜잭션 관리**: 코드와 트랜잭션 로직 분리
- **AOP 기반**: 프록시를 통한 자동 적용
- **유연한 설정**: 다양한 속성을 통한 세밀한 제어

## 2. 어노테이션 적용 위치

### 클래스 레벨 적용
```java
@Service
@Transactional
public class UserService {
    // 모든 public 메서드에 트랜잭션 적용
    public void method1() { }
    public void method2() { }
    private void method3() { } // private 메서드는 적용되지 않음
}
```

### 메서드 레벨 적용
```java
@Service
public class UserService {
    
    @Transactional
    public void transactionalMethod() {
        // 이 메서드만 트랜잭션 적용
    }
    
    public void nonTransactionalMethod() {
        // 트랜잭션 적용되지 않음
    }
}
```

### 우선순위
메서드 레벨 설정이 클래스 레벨 설정보다 우선합니다.

```java
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Transactional(readOnly = false)
    public void writeMethod() {
        // readOnly = false로 적용됨
    }
    
    public void readMethod() {
        // readOnly = true로 적용됨 (클래스 레벨 상속)
    }
}
```

## 3. @Transactional 속성들

### 3.1 propagation (전파)
트랜잭션 전파 방식을 설정합니다.

```java
@Transactional(propagation = Propagation.REQUIRED)
public void method1() {
    // 기본값, 기존 트랜잭션이 있으면 참여, 없으면 새로 생성
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method2() {
    // 항상 새로운 트랜잭션 생성
}

@Transactional(propagation = Propagation.SUPPORTS)
public void method3() {
    // 기존 트랜잭션이 있으면 참여, 없으면 트랜잭션 없이 실행
}

@Transactional(propagation = Propagation.NOT_SUPPORTED)
public void method4() {
    // 트랜잭션 없이 실행, 기존 트랜잭션 일시 중단
}

@Transactional(propagation = Propagation.MANDATORY)
public void method5() {
    // 기존 트랜잭션이 있어야 함, 없으면 예외 발생
}

@Transactional(propagation = Propagation.NEVER)
public void method6() {
    // 트랜잭션 없이 실행, 기존 트랜잭션이 있으면 예외 발생
}

@Transactional(propagation = Propagation.NESTED)
public void method7() {
    // 중첩 트랜잭션 생성 (저장점 사용)
}
```

### 3.2 isolation (격리 수준)
트랜잭션 격리 수준을 설정합니다.

```java
@Transactional(isolation = Isolation.DEFAULT)
public void method1() {
    // 데이터베이스 기본 격리 수준 사용
}

@Transactional(isolation = Isolation.READ_UNCOMMITTED)
public void method2() {
    // 가장 낮은 격리 수준, Dirty Read 가능
}

@Transactional(isolation = Isolation.READ_COMMITTED)
public void method3() {
    // 커밋된 데이터만 읽기, Dirty Read 방지
}

@Transactional(isolation = Isolation.REPEATABLE_READ)
public void method4() {
    // 반복 읽기 일관성 보장, Phantom Read 가능
}

@Transactional(isolation = Isolation.SERIALIZABLE)
public void method5() {
    // 가장 높은 격리 수준, 모든 문제 방지
}
```

### 3.3 timeout (타임아웃)
트랜잭션 타임아웃을 초 단위로 설정합니다.

```java
@Transactional(timeout = 30)
public void longRunningMethod() {
    // 30초 후 타임아웃
}

@Transactional(timeout = -1)
public void noTimeoutMethod() {
    // 타임아웃 없음 (기본값)
}
```

### 3.4 readOnly (읽기 전용)
읽기 전용 트랜잭션으로 설정합니다.

```java
@Transactional(readOnly = true)
public List<User> findAllUsers() {
    // 읽기 전용, 성능 최적화
    return userRepository.findAll();
}

@Transactional(readOnly = false)
public User saveUser(User user) {
    // 쓰기 작업 가능
    return userRepository.save(user);
}
```

### 3.5 rollbackFor / noRollbackFor
롤백 조건을 설정합니다.

```java
@Transactional(rollbackFor = {SQLException.class, DataAccessException.class})
public void method1() {
    // 지정된 예외 발생 시 롤백
}

@Transactional(noRollbackFor = {IllegalArgumentException.class})
public void method2() {
    // 지정된 예외 발생 시 롤백하지 않음
}

@Transactional(rollbackFor = Exception.class)
public void method3() {
    // 모든 예외 발생 시 롤백
}
```

## 4. 트랜잭션 동작 과정

### 4.1 메서드 호출 전
```java
// 1. 트랜잭션 상태 확인
TransactionStatus status = transactionManager.getTransaction(definition);

// 2. 트랜잭션 시작
if (status.isNewTransaction()) {
    // 새로운 트랜잭션 시작
    connection.setAutoCommit(false);
}

// 3. 트랜잭션 동기화 등록
TransactionSynchronizationManager.bindResource(dataSource, connection);
```

### 4.2 메서드 실행 중
```java
// 비즈니스 로직 실행
Object result = method.invoke(target, args);
```

### 4.3 메서드 호출 후
```java
// 1. 예외 발생 여부 확인
if (exception != null) {
    // 롤백 처리
    transactionManager.rollback(status);
} else {
    // 커밋 처리
    transactionManager.commit(status);
}

// 2. 트랜잭션 동기화 정리
TransactionSynchronizationManager.unbindResource(dataSource);
```

## 5. AOP를 통한 트랜잭션 적용

### 프록시 패턴
```java
// 실제 서비스 클래스
@Service
public class UserServiceImpl implements UserService {
    @Transactional
    public void saveUser(User user) {
        // 실제 비즈니스 로직
    }
}

// 스프링이 생성하는 프록시 클래스 (개념적)
public class UserServiceProxy implements UserService {
    private UserServiceImpl target;
    private TransactionManager transactionManager;
    
    public void saveUser(User user) {
        // 트랜잭션 시작
        TransactionStatus status = transactionManager.getTransaction(definition);
        try {
            // 실제 메서드 호출
            target.saveUser(user);
            // 커밋
            transactionManager.commit(status);
        } catch (Exception e) {
            // 롤백
            transactionManager.rollback(status);
            throw e;
        }
    }
}
```

### 인터셉터 체인
```java
// 트랜잭션 인터셉터
public class TransactionInterceptor implements MethodInterceptor {
    
    public Object invoke(MethodInvocation invocation) throws Throwable {
        // Before: 트랜잭션 시작
        TransactionStatus status = beginTransaction();
        
        try {
            // 실제 메서드 호출
            Object result = invocation.proceed();
            
            // After: 커밋
            commitTransaction(status);
            return result;
            
        } catch (Exception e) {
            // After Throwing: 롤백
            rollbackTransaction(status);
            throw e;
        }
    }
}
```

## 6. 실제 사용 예제

### 6.1 기본 CRUD 서비스
```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Transactional(readOnly = true)
    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found"));
    }
    
    @Transactional(readOnly = true)
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    @Transactional
    public User save(User user) {
        validateUser(user);
        return userRepository.save(user);
    }
    
    @Transactional
    public void deleteById(Long id) {
        User user = findById(id);
        userRepository.delete(user);
    }
    
    @Transactional
    public User updateUser(Long id, User updatedUser) {
        User existingUser = findById(id);
        existingUser.setName(updatedUser.getName());
        existingUser.setEmail(updatedUser.getEmail());
        return userRepository.save(existingUser);
    }
    
    private void validateUser(User user) {
        if (user.getName() == null || user.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("User name cannot be empty");
        }
        if (user.getEmail() == null || !user.getEmail().contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
}
```

### 6.2 복잡한 비즈니스 로직
```java
@Service
@Transactional
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private ProductService productService;
    
    @Transactional(
        propagation = Propagation.REQUIRED,
        isolation = Isolation.READ_COMMITTED,
        timeout = 30,
        rollbackFor = {InsufficientStockException.class, PaymentException.class}
    )
    public Order createOrder(Long userId, List<OrderItem> items) {
        // 1. 사용자 검증
        User user = userService.findById(userId);
        
        // 2. 재고 확인 및 차감
        for (OrderItem item : items) {
            productService.checkAndReserveStock(item.getProductId(), item.getQuantity());
        }
        
        // 3. 주문 생성
        Order order = new Order();
        order.setUserId(userId);
        order.setItems(items);
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());
        
        Order savedOrder = orderRepository.save(order);
        
        // 4. 결제 처리
        try {
            processPayment(savedOrder);
            savedOrder.setStatus(OrderStatus.CONFIRMED);
        } catch (PaymentException e) {
            // 결제 실패 시 재고 복구
            restoreStock(items);
            throw e;
        }
        
        return orderRepository.save(savedOrder);
    }
    
    private void processPayment(Order order) {
        // 결제 처리 로직
    }
    
    private void restoreStock(List<OrderItem> items) {
        // 재고 복구 로직
    }
}
```

## 7. 주의사항 및 베스트 프랙티스

### 7.1 메서드 가시성
```java
@Service
public class UserService {
    
    @Transactional
    public void publicMethod() {
        // 트랜잭션 적용됨
    }
    
    @Transactional
    protected void protectedMethod() {
        // 트랜잭션 적용됨
    }
    
    @Transactional
    private void privateMethod() {
        // 트랜잭션 적용되지 않음! (AOP 제한)
    }
}
```

### 7.2 self-invocation 문제
```java
@Service
public class UserService {
    
    @Transactional
    public void method1() {
        // this.method2()는 프록시를 거치지 않음
        this.method2(); // 트랜잭션 적용되지 않음!
    }
    
    @Transactional
    public void method2() {
        // 트랜잭션 적용되지 않음
    }
}

// 해결 방법: 자기 자신을 주입
@Service
public class UserService {
    
    @Autowired
    private UserService self; // 자기 자신 주입
    
    @Transactional
    public void method1() {
        self.method2(); // 프록시를 통해 호출
    }
    
    @Transactional
    public void method2() {
        // 트랜잭션 적용됨
    }
}
```

### 7.3 예외 처리
```java
@Service
public class UserService {
    
    @Transactional
    public void methodWithException() {
        try {
            // 비즈니스 로직
            throw new RuntimeException("Error occurred");
        } catch (RuntimeException e) {
            // 예외를 잡아서 처리하면 롤백되지 않음!
            log.error("Error occurred", e);
            // 트랜잭션은 커밋됨
        }
    }
    
    @Transactional
    public void methodWithProperExceptionHandling() {
        try {
            // 비즈니스 로직
            throw new RuntimeException("Error occurred");
        } catch (RuntimeException e) {
            log.error("Error occurred", e);
            // 예외를 다시 던져야 롤백됨
            throw e;
        }
    }
}
```

이제 다음 학습 자료에서 트랜잭션 생명주기에 대해 더 자세히 알아보겠습니다.
